import os
import sys
import json
import pandas as pd
import imaplib
# import email
from email import message_from_bytes, message_from_string
from email import header
import getpass
import re
import streamlit as st
# import openpyxl
import yaml
from datetime import datetime
import numpy as np
now = datetime.now()
from utils import utils
from utils import visualize_po_db
from itertools import chain
# from PO_streamlit_client.cred_data import gmail.cred

# with open('.gmail_pred.yml') as f:
#      cred = f.read()
#
my_logo = utils.add_logo(logo_path="imgs/Kalika logo.png", width=300, height=60)
st.sidebar.image(my_logo)

st.title("Kalika SMART Email Poller")

# my_credentials = yaml.load(cred, Loader = yaml.FullLoader)
uid_max = 0


class Email_extractor:
    def __init__(self):
        self.user = st.secrets["gmail_uname"]
        self.password = st.secrets["gmail_pwd"]
        self.data = []
        self.destFolder = './data/pdf_data/'
        self.destFolder2 = './data/json_data/'

    def get_login(self):
        print("\nPlease enter your Gmail login details below.")
        self.usr = input("Email: ")
        self.pwd = input("Password: ")

    def attempt_login(self):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.user, self.password)

    def select_mail(self):
        self.data = self.mail.select("inbox")
        mail_ids = self.data[1]
        id_list = mail_ids[0].split()

    def search_with_mailid(self, key, value):
        result, self.data = self.mail.search(None, key, '"{}"'.format(value))
        return self.data

    def get_email(self, result_bytes):

        date_list = []
        from_list = []
        subject_text = []

        uids = result_bytes[0].split()
        uids = [id.decode("utf-8") for id in uids]
        print("UID", uids[2], len(uids))
        uids = uids[-1:-201:-1]

        print("Latest UID", uids[2], len(uids))
        result, messages = self.mail.uid('fetch', ','.join(uids), '(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
        messages = [i for i in messages if isinstance(i, tuple)]
        for i, message in messages[::2]:
            try:
                msg = message_from_bytes(message)

                decode = header.decode_header(msg['Subject'])[0]

                if isinstance(decode[0], bytes):
                    decoded = decode[0].decode()
                    subject_text.append(decoded)
                else:
                    subject_text.append(decode[0])
                date_list.append(msg.get('date'))
                fromlist = msg.get('From')
                fromlist = fromlist.split("<")[0].replace('"', '')
                from_list.append(fromlist)
            except Exception as e:
                print(e)
                pass

        date_list = pd.to_datetime(date_list,format="mixed")
        date_list1 = []
        for item in date_list:
            date_list1.append(item.isoformat(' ')[:-6])

        df = pd.DataFrame(data={'Date': date_list1, 'Sender': from_list, 'Subject': subject_text})
        return df

    def mail_extract(self, search=True):
        date_list = []
        from_list = []
        subject_text = []
        if search:
            result, numbers = self.mail.uid('search', None, "ALL")
            print(len(numbers))
            df = self.get_email(numbers)
            return df

    def search_string(self,uid_max, criteria):
        c = list(map(lambda t: (t[0], '"' + str(t[1]) + '"'), criteria.items())) + [('UID', '%d:*' % (uid_max + 1))]
        return '(%s)' % ' '.join(chain(*c))
        # Produce search string in IMAP format:
        #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)

    # Get any attachemt related to the new mail
    def parseEmails(self, key, value):
        jsonOutput = {}
        json_list = []
        #         type, self.data = self.mail.search(None, "ALL")
        result, self.data = self.mail.search(None, key, '"{}"'.format(value))

        filename = ""

        for anEmail in self.data[0].split()[:10]:
            type, self.data = self.mail.fetch(anEmail, '(UID RFC822)')
            raw = self.data[0][1]
            try:
                raw_str = raw.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    raw_str = raw.decode("ISO-8859-1")  # ANSI support
                except UnicodeDecodeError:
                    try:
                        raw_str = raw.decode("ascii")  # ASCII ?
                    except UnicodeDecodeError:
                        pass

            msg = message_from_string(raw_str)

            jsonOutput['subject'] = msg['subject']
            jsonOutput['from'] = msg['from']
            jsonOutput['date'] = msg['date']

            filename = str(msg['from'])
            filename = re.sub('<.*>', '', filename)
            filename = re.sub('[^A-Za-z0-9]+', ' ', filename)
            filename = filename + '.pdf'
            filename = filename.replace(' .pdf', '.pdf')
            print('Clean_filename', filename)
            raw = self.data[0][0]
            raw_str = raw.decode("utf-8")
            uid = raw_str.split()[2]

            # Body #
            if msg.is_multipart():
                for part in msg.walk():
                    partType = part.get_content_type()
                    ## Get Body ##
                    if partType == "text/plain" and "attachment" not in part:
                        jsonOutput['body'] = part.get_payload()

                    if partType == 'application/pdf':
                        print("Found pdf")
                        payload = part.get_payload(decode=True)

                        #                         filename = part.get_filename()
                        #                         if 'utf' in filename:
                        #                             filename=str(uid)
                        #                             print(filename)

                        # Save the file.
                        if payload and filename:
                            attchFilePath = str(self.destFolder) + str(uid) + str("/") + str(filename)
                            os.makedirs(os.path.dirname(attchFilePath), exist_ok=True)
                            with open(attchFilePath, 'wb') as f:
                                f.write(payload)

                                ## Get Attachments ##
                                if part.get('Content-Disposition') is None:
                                    attchName = part.get_filename()
                                    if bool(attchName):
                                        attchFilePath = str(self.destFolder)+str(uid)+str("/")+str(attchName)
                                        os.makedirs(os.path.dirname(attchFilePath), exist_ok=True)
                                        with open(attchFilePath, "wb") as f:
                                            f.write(part.get_payload(decode=True))

            else:
                try:
                    jsonOutput['body'] = msg.get_payload(decode=True).decode(
                        "utf-8")  # Non-multipart email, perhaps no attachments or just text.

                except Exception as e:
                    jsonOutput['body'] = msg.get_payload(decode=True).decode(
                        "ISO-8859-1")  # Non-multipart email, perhaps no attachments or just text.

                    print(e)
                    pass
            outputDump = json.dumps(jsonOutput)
            json_list.append(outputDump)

            emailInfoFilePath = str(self.destFolder2) + str(uid) + str("/") + str(uid) + str(".json")
            os.makedirs(os.path.dirname(emailInfoFilePath), exist_ok=True)
            with open(emailInfoFilePath, "w") as f:
                f.write(outputDump)

    def preprocess(self,df,col):
        df[col] = df[col].apply(lambda x: re.sub(r'[^\w\s]', '', x))
        df[col] = df[col].apply(lambda x: re.sub('[^A-Za-z0-9]+', ' ',x))

        return df

    def postprocess(self,df,col1):
        # df[col1] = df[col1].replace(' ',"Bank email")
        df[col] = df[col1].apply(lambda x: re.sub(r"=.*", '', x))
        df[col] = df[col1].apply(lambda x: re.sub('[^A-Za-z0-9]+', ' ', x))
        df[col]= df[col1].replace('',np.nan).fillna("Bank")

        return df


    def subject_category(self,text):
        category=''
        text=text.lower()
        if "quote" in text:
            category="quote"
        elif "purchase" in text:
            category="po"
        elif "invoice" in text:
            category="invoice"
        else:
            category = "other"
        return category

    def categorize(self,df,col):
        """

        """
        df["Category"]=df[col].apply(lambda x:self.subject_category(x))

        return df

# class NLP_pipeline:
#     def __init__(self, gmail_df):
#         self.df = gmail_df
#
#     def preprocess(self,df, col):
#         self.df['col'] = self.df['sender'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
#         return df


if __name__ == "__main__":
    email = Email_extractor(my_credentials)
    email.attempt_login()
    email.select_mail()

    all_latest,search_key,pdf_body_attachment=st.tabs(["all_latest", "search_keys", "search_key_pdf_body_data"])
    res=''
    keyword=''
    with all_latest:

        df = email.mail_extract()  ## all recent 200
        cols=df.columns
        col=st.selectbox('columns to replace empty values',cols[1:])
        df = email.postprocess(df,col1=col)
        st.table(df.head(10))
        ddf=df[["Date","Sender"]]
        st.bar_chart(ddf,x="Date",y="Sender")

    with search_key:

        co=st.text_input("Enter the search key to fetch email")
        option = st.selectbox('Filter to Search',('SUBJECT',"FROM"))

        if co:
            if option=="FROM":
                keyword='*@'+co+'*.com'
                res=email.search_with_mailid(option, keyword) ## on keyword recent 200
            if option=="SUBJECT":
                keyword='subject:'+co
                res=email.search_with_mailid(key="X-GM-RAW", value=keyword) ## on keyword recent 200
            search_df = email.get_email(res)
            cols=search_df.columns
            column=st.selectbox("columns for preprocess",cols[1:])

            search_df = email.preprocess(df=search_df,col=column)
            date = now.strftime("%m_%d_%Y")


            search_df=email.categorize(search_df,col="Subject")

            ddf = search_df[["Sender","Category"]]
            ddf= ddf.set_index("Category")
            ddf= ddf.groupby("Category").sum()

            st.table(search_df.head(3))
            # st.pyplot(ddf.plot.barh(stacked=True).figure)
            st.bar_chart(ddf)

            search_df=search_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Press to Download",
                data=search_df,
                file_name="search"+keyword+"_"+date+".csv",
                mime="text/csv",
                key='download-csv'
            )

    with pdf_body_attachment:
        # st.write('test')
        co=st.text_input("Enter filter based on keyword",'cummins')
        if co:
            keyword = '*@' + co + '*.com'
            email.parseEmails('FROM',keyword)



