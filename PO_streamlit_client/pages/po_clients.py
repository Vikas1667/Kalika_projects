import sys,os
import pandas as pd
import streamlit as st
import altair as alt
import base64
import matplotlib.pyplot as pltt
print(os.getcwd())
# V:\ML_projects\github_projects\Purchase-Order-Application\PO_streamlit_client
# from .PO_streamlit_client import mongo_connection
import mongo_connection
from PIL import Image

from utils import utils


my_logo = utils.add_logo(logo_path=r"imgs/Kalikalogo.png", width=300, height=60)
st.image(my_logo)
st.title("PO TRACKER")

PO = st.text_input("Enter your PO Number"," ")
Item = st.text_input("Enter your item "," ")
df_list=[]


if PO:

    plot_items=['Quantity Ordered','Quantity Shipped','Quantity Received','PENDING']
    df_list=[]
    columns = ["PO Number", "Item No", "Item Description", "Quantity Shipped"]

    if st.button("Track"):
        st.write("PO_DB connect inprogress")
        po_status_data = mongo_connection.find_with_po(PO)
        st.write(po_status_data)

        df=mongo_connection.records_dataframe(po_status_data)

        if len(df)>0:
            st.table(df)
            st.write(df['Material Status'])
        # if po_status_data:
        #     for k,v in po_status_data():
        #         st.write(k,"-->",v)

            # po_df=pd.DataFrame(po_status_data.items())
            # st.table(po_df)

            # Altair_Figure = alt.Chart(po_df).mark_circle().encode(
            #     x=po_df['Quantity Ordered'],
            # y = range(-5,2,100))
            # st.bar_chart(po_df,height=205,width=40)
            # st.altair_chart(Altair_Figure)
    # st.write(po_status_data)

