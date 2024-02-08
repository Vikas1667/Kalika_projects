from langchain.document_loaders import CSVLoader
# from transformers import GPT3Tokenizer, GPT3ChatLM
import pandas as pd
import streamlit as st

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

    # st.write(df.columns)

    df["Material Status Yet to Order"]=[True for i in range(len(df))]
    df["Material Status in Transport"]=[False for i in range(len(df))]
    df["Material Status Delivered"]=[False for i in range(len(df))]

    df["Transport details"] = ""
    df["Vendor details"]=""
    df['PO_data_date']=pd.datetime.now().strftime("%d/%m/%Y")

    df.insert(0, 'PO_data_date', df.pop('PO_data_date'))
    # df = df.loc[~df.index.duplicated(), :].copy()

    # df=[
    #     {"command": "st.selectbox", "rating": 4, "is_widget": True},
    #     {"command": "st.balloons", "rating": 5, "is_widget": False},
    #     {"command": "st.time_input", "rating": 3, "is_widget": True},
    # ]
    ## check duplicate columns
    # https: // blog.streamlit.io / editable - dataframes - are - here /
    st.data_editor(df,num_rows="dynamic")
    # st.write(df["Material Status Yet to Order"][0])
    st.write(df["Material Status Yet to Order"][0])

