import pymongo
from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
import streamlit as st
import pandas as pd
import logging
import json

# with open('auth.json') as js:
#     db=json.load(js)
#     db_username=db["db_username"]
#     db_pswd =db["db_pswd"]

logging.basicConfig(filename='app_logger.log', encoding='utf-8', level=logging.DEBUG,filemode="w")

# Create a new client and connect to the  server
uname=st.secrets["db_username"]
pwd=st.secrets["db_pswd"]

uri = "mongodb+srv://"+uname+":"+pwd+"@cluster0.pkysva5.mongodb.net/?retryWrites=true&w=majority"

# @st.experimental_singleton()
def init_connection():
    return MongoClient(uri,connect=False)

try:
    client = init_connection()
    mng_db = client['kalika_data']
    collection_name='kalika_po'
    # collection_name='po_admin'

    db_cm = mng_db[collection_name]
except Exception as e:
    logging.error('Unable to connect to DB please update the ip address in DB')


def find_mongo():
    records = db_cm.find()
    df=pd.DataFrame(list(records))
    return df

def insert_data(df):
    try:
        data_json = json.loads(df.to_json(orient='records'))
        db_cm.insert_many(data_json)
    except Exception as e:
        logging.error(e)
        st.write('Some Issue Please Try again or Contact to get Tracing details')

def find_with_po(po_number):
    try:
        db_cm = mng_db[collection_name]
        result = db_cm.find({'PO Number': po_number})
        st.write('{} records found'.format(result.count()))

        if result.count()>0:
            return result

        else:
            st.write("No document Found with PO number{}".format(po_number))
            return None


    except Exception as e:
        logging.error(e)
        st.write('Check PO number or No data for PO you enter')
        return "Connection error due to{}".format(e)


def records_dataframe(po_status_data):
    df_list=[]
    if po_status_data:
        for doc in po_status_data:
            df_list.append(doc)
        df = pd.DataFrame(df_list)
        return df

def unique_records(df,key='PO'):

    po_list=df['PO Number'].tolist()
    r=db_cm.find()
    po_df=pd.DataFrame(list(r))

    if len(po_df)>0:
        po_dup=po_df[po_df['PO Number'].isin(po_list)]
        st.write("Records already exists for below PO",po_dup)
        po_unq = po_df[~po_df['PO Number'].isin(po_list)]
        return po_unq

    else:
        st.write("No Duplicate or new records are detected")
        return po_df


def update_records(query,updated_val,po):

    try:
        db_cm.update(query,updated_val)
        po_status_data = find_with_po(po)
        df = records_dataframe(po_status_data)
        st.write('Updated the values', df)

        return "Update successful"

    except Exception as e:
        st.write('Update issue')
