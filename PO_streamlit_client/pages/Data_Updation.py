import os, sys
import streamlit as st
import pandas as pd
# import streamlit_authenticator as stauth
# import yaml
# from yaml.loader import SafeLoader

from PIL import Image
import time
# st.write(os.getcwd())
sys.path.append('../')
import mongo_connection
from mongo_connection import insert_data,update_records,records_dataframe
from utils import utils

# update_columns

val = ['Quantity Shipped', 'Material Status', "Transport details "]


my_logo = utils.add_logo(r"./imgs/Kalikalogo.png", width=300, height=60)
st.image(my_logo)

st.header(':blue[Insert] or :orange[Update] PO Data with _ease_ :sunglasses:')


def file_upload():

    # st.header('Upload_PO_Excel for clients to Track')
    uploaded_file = st.file_uploader('Upload a file')
    if uploaded_file is not None:
        st.write(uploaded_file)
        df = pd.read_excel(uploaded_file)
        st.write(df)
        # update_columns(df, val)
        # df['Due Date'] = df['Due Date'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        df['Due Date'] = pd.to_datetime(df['Due Date'], errors='ignore')
        return df



def insert_po_details(po_no):

    po_df=pd.DataFrame()
    st.write("PO records not exists proceed")
    po_df['po_no'] = st.text_input("PO Number:", po_no)
    po_df['item_no'] = st.text_input("Item_Number:", 'Enter the item number')
    po_df['SupplierItem']=st.text_input("SupplierItem:", 'Enter the Supplier item')
    po_df['ItemDescription'] = st.text_input("ItemDescription:", 'Enter the ItemDescription')

    po_df['DueDate'] = st.text_input("Due Date:", 'Enter the Due Date')
    po_df['QuantityOrdered'] = st.text_input("Quantity Ordered:", 'Enter the Quantity Ordered')
    po_df['QuantityReceived'] = st.text_input("ItemDescription:", 'Enter the Quantity Received')
    po_df['PENDING'] = st.text_input("PENDING:", 'Enter the PENDING items')
    po_df['UOM'] = st.text_input("UOM:", 'Enter the UOM')
    po_df['MaterialStatus']=st.text_input("MaterialStatus:", 'Enter the UOM')
    po_df['Transportdetails']=st.text_input("Transport details:", 'Enter the Transport details')
    # st.write(po_df)
    return po_df


def update_records(po):
    '''
       upload the po_file if duplicate po_no exist no of records are displayed and if not present inserted
       ## scenarios
       1. if some records/rows/po_number are duplicate
       -> uniques records are inserted with matching/find and then removing matched records(done)
           i) po_matched but items/products can be different and removed directly with check of po_only
           --> if matched other fields can be check(inprogress)

       '''

    if po:
        po_status_data = mongo_connection.find_with_po(po)
        if po_status_data:
            df = mongo_connection.records_dataframe(po_status_data)
            st.write('Update the values')

            item_details = ['Supplier Item', "Item No", "Due Date"]
            key = time.time()
            widget_id = (id for id in range(1, 100_00))
            df=df.fillna("NOT")
            # st.table(df[['PO Number', 'Item No', 'Item Description', 'Quantity Ordered', 'Material Status']])
            query_update_dict = []
            for i, v in zip(item_details, val):
                ma_ = st.checkbox(v)
                key = time.time()
                if ma_:
                    updated_placeholder.append(v)
                    for ind, val in df.iterrows():
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write('current value for {} is :-->{}'.format(val[i], val[v]))
                        with col2:
                            new_value = st.text_input('update value', key=next(widget_id))
                            st.write(new_value)
                            if new_value != None and new_value != '':
                                update_tup = (v, val[v], new_value)
                                query_update_dict.append(update_tup)

            if st.button('Update Records', key=next(widget_id)):
                st.write(len(query_update_dict))
                for k in query_update_dict:
                    # st.write(k)
                    st.write('case', k[0])
                    query = {k[0]: k[1]}
                    update = {"$set": {k[0]: k[2]}}
                    updated_msg = update_records(query, update, po)
                    # st.write(updated_msg)
            #
            # if po_status_data:
            #     st.write(po_status_data)


if __name__ == '__main__':

    updated_placeholder = []
    updated_df = pd.DataFrame()
    # st.subheader('Insert your PO Excel to check exist and Insert if not exist')
    st.markdown('Insert your PO Excel to check exist and Insert if not exist')
    po_no = st.text_input("PO_Number:")

    cols1,cols2=st.columns([1, 1])
    cols = ['insert data', 'Update_records', 'Delete']


    with cols1:
        uploadbtn =st.button('PO file upload')

    with cols2:
        rec_exist = st.button("check if po records exist")
        po_status_data = mongo_connection.find_with_po(po_no)
        df=records_dataframe(po_status_data)
        if df is not None:
            st.write(df)


    if "uploadbtn_state" not in st.session_state:
            st.session_state.uploadbtn_state = False

    if uploadbtn or st.session_state.uploadbtn_state:
        st.session_state.uploadbtn_state = True

        df = file_upload()

        if df is not None:
            unq_rec=mongo_connection.unique_records(df)
            st.write('Inserting all uniques values')
            if len(unq_rec)>0:
                st.write('Inserting all uniques values')
                mongo_connection.insert_data(unq_rec)

            else:
                st.write('All Duplicate Records found..')
                # mongo_connection.insert_data(df)


            # # st.write('')
            st.subheader('Enter the records manually _or Update_ :blue[colors] and emojis :sunglasses:')


            po_data=[i for i in po_status_data]
            df=pd.DataFrame(po_data)

    if len(df) > 0:
        col1, col2 = st.columns(2)  # Split the screen into two columns
        
        with col1:
            upload_button = st.button('Update Current Status for PO')
            if upload_button:
                update_records(po_no)

        with col2:
            insert_button = st.button('Insert the data manually')
            if insert_button:
                po = insert_po_details(po_no)


