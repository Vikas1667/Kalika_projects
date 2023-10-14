# from transformers import T5Tokenizer, T5ForConditionalGeneration
import streamlit as st
import sys,os
import pandas as pd
import streamlit as st
import altair as alt
import base64
import matplotlib.pyplot as pltt
print(os.getcwd())
import mongo_connection
import altair as alt
import matplotlib.pyplot as plt

from utils import utils
from utils import visualize_po_db

my_logo = utils.add_logo(logo_path="imgs/Kalika logo.png", width=300, height=60)
st.sidebar.image(my_logo)
# st.image(my_logo)

st.title("Kalika SMART Procurement")


tab1, tab2 = st.tabs(["Buyer Analysis", "Generate smart item description"])
df=visualize_po_db.mongo_records_poller()

with tab1:
    # st.table(df.head(5))
    chunk_df=df[:20]

    item_status_df=chunk_df[['Item Description','Quantity Ordered','Quantity Received','PENDING']]
    po_status_df=chunk_df[['PO Number','Quantity Ordered','Quantity Received','PENDING']]

    item_status_df['Item Description']=item_status_df['Item Description'].apply(lambda x:' '.join(x.split()[:3]))
    ##


    item_status_df=item_status_df.set_index('Item Description')
    po_status_df = po_status_df.set_index('PO Number')
    po_status_df=po_status_df.groupby(['PO Number']).sum()
    item_status_df= item_status_df.groupby(['Item Description']).sum()



    st.pyplot(po_status_df.plot.barh(stacked=True).figure)
    st.pyplot(item_status_df.plot.barh(stacked=True,).figure)
    # figsize=(20, 25)
with tab2:
    st.write('Model for creating Item description')

