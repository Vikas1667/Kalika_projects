#!/usr/bin/env python
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from streamlit_chat import message
import pandas as pd
import streamlit as st
from typing import TypedDict
from dataclasses import dataclass
from pandasai.llm.starcoder import Starcoder
from pandasai.llm.starcoder import Starcoder
# from pandasai.llm.open_assistant import OpenAssistant
# from pandasai.llm.falcon import Fal
from transformers import pipeline
from utils import utils


my_logo = utils.add_logo(logo_path="imgs/Kalikalogo.png", width=300, height=60)
st.image(my_logo)

@st.cache_resource
def tapas_model(data,prompt):

    tqa = pipeline(task="table-question-answering", model="google/tapas-large-finetuned-wtq")
    response = tqa(table=data, query=prompt)['cells'][0]
    return response


@st.cache_resource
def data_prep(df):
    ## generalize for datatype if datetime of column
    integer_dtype=["Quantity Ordered","Quantity Shipped","Quantity Received", "PENDING"]
    df=df.fillna("No Data")
    df['Due Date'] = df['Due Date'].dt.strftime('%Y-%m-%d')
    for i in integer_dtype:
        df[i]=df[i].astype(str)

    return df

def data_modeling(df):
    '''

    :param df:
    :return:
    as df has multiple rows for single row i.e. one po_number
    issues
    1. tapas model fetch first rows
    -> groupby and aggregate to dictionary and then map to required response
    2. given wrong po_number is given
    --> po_number check
    '''
    pass

@dataclass
class Message:
    actor: str
    payload: str

USER="user"
ASSISTANT="assistant"
MESSAGES="messages"
# openai_key=st.secrets["openai_key"]

if __name__ == "__main__":
    if MESSAGES not in st.session_state:
        st.session_state[MESSAGES]=[Message(actor=ASSISTANT,payload="How Can I help you")]

    msg:Message
    for msg in st.session_state[MESSAGES]:
        st.chat_message(msg.actor).write(msg.payload)

    if "past" not in st.session_state:
        st.session_state['past']=[]

    openai_key=st.sidebar.text_input("Enter the openai_key")
    train_df=pd.read_excel(r"../sample_data/28 JUNE 2023 CFS.xlsx")

    # llm=Starcoder(api_token=openai_key)

    prompt:str=st.chat_input("Enter the PO number for status")
    uploaded_file = st.sidebar.file_uploader('Upload a csv or excel file',type=["xlsx","csv","txt"])

    if prompt and openai_key:
        llm = OpenAI(api_token=openai_key)
        st.session_state[MESSAGES].append(Message(actor=USER,payload=prompt))
        st.chat_message(USER).write(prompt)
        df=SmartDataframe(train_df,config={"llm":llm})
        response:str=f"Your PO number as response{prompt}"

        response=df.chat(prompt)
        if response:

            st.session_state[MESSAGES].append(Message(actor=ASSISTANT,payload=response))
            st.chat_message(ASSISTANT).write(response)

        else:
            st.write("Rephrase the query")


    elif uploaded_file is not None:
        df=pd.DataFrame()
        try:
            df=pd.read_csv(uploaded_file)
        except:
            df = pd.read_excel(uploaded_file)


    if df is not None and len(df)>0:

        df=data_prep(df)
        data=df.to_dict('list')
        # st.write(data)
        st.write(df)
        if prompt is not None:
            # prompt=f"What is the Quantity Ordered for po number {prompt}"
            # prompt=f"What is the Material Status for po number {prompt}"
            # prompt=f"Fetch all details for po number {prompt}"

            st.session_state[MESSAGES].append(Message(actor=USER, payload=prompt))
            response=tapas_model(data=df,prompt=prompt)
            # st.write(response)

            st.chat_message(USER).write(prompt)


            if response:
                st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
                st.chat_message(ASSISTANT).write(response)
            else:
                st.write("Rephrase the query")
        # print(tqa(table=df, query=prompt)['cells'][0])

        # if prompt:
        #     comp_promp = f"What is the Material status for PO number {prompt}"
        #     st.session_state[MESSAGES].append(Message(actor=USER, payload=comp_promp))
        #     st.chat_message(USER).write(comp_promp)
