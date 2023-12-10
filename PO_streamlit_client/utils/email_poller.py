import os
import sys
import json
import pandas as pd
import imaplib
# import email
from email import message_from_bytes,message_from_string
from email import header
import getpass
import re
import yaml
import streamlit as st

# yml_path=os.path.join(os.getcwd(),r"cred_data\gmail_cred.yml")
# st.write(yml_path)
yml_path=r"D:\ML_Project\Kalika_projects\PO_streamlit_client\cred_data/gmail_pred.yml"

with open(yml_path) as f:
     cred = f.read()


my_credentials = yaml.load(cred, Loader = yaml.FullLoader)
imap_url = 'imap.gmail.com'


class Email_extractor:
    def __init__(self,my_credentials):
        self.user=my_credentials["username"]
        self.password = my_credentials['password']
        self.data = []

    def get_login(self):
        print("\nPlease enter your Gmail login details below.")
        self.usr = input("Email: ")
        self.pwd = input("Password: ")


    def attempt_login(self):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.user, self.password)

    def select_mail(self):

        self.data=self.mail.select("inbox")

        # print(type(self.data[1]), len(self.data[0]))
        mail_ids = self.data[1]
        id_list = mail_ids[0].split()
        print('Ids extracted',id_list)


    def mail_extract(self):
        date_list = []
        from_list = []
        subject_text = []

        result, numbers = self.mail.uid('search', None, "ALL")
        uids = numbers[0].split()
        uids = [id.decode("utf-8") for id in uids]
        uids = uids[-1:-101:-1]
        print("Latest mailids",uids)
        result, messages = self.mail.uid('fetch', ','.join(uids), '(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
        messages = [i for i in messages if isinstance(i, tuple)]
        st.write(messages)

        for i, message in messages[::2]:
            try:
                msg = message_from_bytes(message)
                print(msg)
                decode = header.decode_header(msg['Subject'])[0]
                print('as', msg, decode)

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
                st.write(e)
                pass

        date_list = pd.to_datetime(date_list,format='mixed')
        date_list1 = []
        for item in date_list:
            date_list1.append(item.isoformat(' ')[:-6])

        df = pd.DataFrame(data={'Date': date_list1, 'Sender': from_list, 'Subject': subject_text})
        st.write(df.head(3))
        return df


    def parseEmails(self):
        self.destFolder='V:/ML_projects/Bussiness/kalika/data/'
        self.destFolder2='V:/ML_projects/Bussiness/kalika/data2/'

        jsonOutput = {}
        json_list = []
        type, self.data = self.mail.search(None, "ALL")
        filename = ""
        for anEmail in self.data[0].split():
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

                    ## get pdf ##
                    if partType == 'application/pdf':
                        print("Found pdf")
                        payload = part.get_payload(decode=True)

                        # Save the file.
                        if payload and filename:
                            attchFilePath = str(self.destFolder) + str(uid) + str("/") + str(filename)
                            os.makedirs(os.path.dirname(attchFilePath), exist_ok=True)
                            with open(attchFilePath, 'wb') as f:
                                f.write(payload)

            #                     ## Get Attachments  for images##
            #                     if part.get('Content-Disposition') is None:
            #                         attchName = part.get_filename()
            #                         if bool(attchName):
            #                             attchFilePath = str(self.destFolder)+str(uid)+str("/")+str(attchName)
            #                             os.makedirs(os.path.dirname(attchFilePath), exist_ok=True)
            #                             with open(attchFilePath, "wb") as f:
            #                                 f.write(part.get_payload(decode=True))

            else:
                jsonOutput['body'] = msg.get_payload(decode=True).decode(
                    "utf-8")  # Non-multipart email, perhaps no attachments or just text.

            outputDump = json.dumps(jsonOutput)
            json_list.append(outputDump)

            emailInfoFilePath = str(self.destFolder2) + str(uid) + str("/") + str(uid) + str(".json")
            os.makedirs(os.path.dirname(emailInfoFilePath), exist_ok=True)
            with open(emailInfoFilePath, "w") as f:
                f.write(outputDump)


if __name__ == "__main__":
    email=Email_extractor(my_credentials)
    email.attempt_login()
    email.select_mail()
    email.mail_extract()




