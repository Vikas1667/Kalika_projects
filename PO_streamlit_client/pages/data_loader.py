from langchain.document_loaders import CSVLoader
# from transformers import GPT3Tokenizer, GPT3ChatLM
import pandas as pd
import streamlit as st
from mongo_connection import upsert_records,delete_all
uploaded_file = st.file_uploader('Upload a file')
# tokenizer = GPT3Tokenizer.from_pretrained("gpt3.5-turbo")
# model = GPT3ChatLM.from_pretrained("gpt3.5-turbo")


# if uploaded_file is not None:
#     st.write(uploaded_file)
#     loader = CSVLoader(uploaded_file)
#     documents = loader.load()
if uploaded_file is not None:
    df=pd.read_excel(uploaded_file)
    # st.table(df.head(2))

    df["Material Status Yet to Order"]=[True for i in range(len(df))]
    df["Material Status in Transport"]=[False for i in range(len(df))]
    df["Material Status Delivered"]=[False for i in range(len(df))]

    df["Transport details"] = ""
    df["Vendor details"]=""
    df['PO_data_date']=pd.datetime.now().strftime("%d/%m/%Y")

    df.insert(0, 'PO_data_date', df.pop('PO_data_date'))
    # df = df.loc[~df.index.duplicated(), :].copy()

    po_df=st.data_editor(df,num_rows="dynamic")

    if po_df is not None:
        if st.button("Insert records"):
            try:
                upsert_records(po_df)

                st.write("Insertion successful")
            except Exception as e:
                st.write('Insertion failed', e)
if st.button("delete records"):
    try:
        delete_all()
        st.write("deleting all records")
    except Exception as e:
        st.write('Deleting operation fail',e)

