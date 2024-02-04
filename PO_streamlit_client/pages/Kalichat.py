from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from streamlit_chat import message
import pandas as pd
import streamlit as st
from typing import TypedDict
from dataclasses import dataclass

@dataclass
class Message:
    actor: str
    payload: str


USER="user"
ASSISTANT="assistant"
MESSAGES="messages"

if __name__ == "__main__":
    if MESSAGES not in st.session_state:
        st.session_state[MESSAGES]=[Message(actor=ASSISTANT,payload="How Can I help you")]

    msg:Message
    for msg in st.session_state[MESSAGES]:
        st.chat_message(msg.actor).write(msg.payload)

    if "past" not in st.session_state:
        st.session_state['past']=[]

    openai_key=st.text_input("Enter the openai_key")
    if openai_key:
        train_df=pd.read_excel(r"../sample_data/28 JUNE 2023 CFS.xlsx")
        llm=OpenAI(api_token=openai_key)

        prompt:str=st.chat_input("Enter the po_no for status")
        if prompt:
            st.session_state[MESSAGES].append(Message(actor=USER,payload=prompt))
            st.chat_message(USER).write(prompt)
            df=SmartDataframe(train_df,config={"llm":llm})
            response:str=f"Your PO number as response{prompt}"

            response=df.chat(prompt)
            if response:

                st.session_state[MESSAGES].append(Message(actor=ASSISTANT,payload=response))
                st.chat_message(ASSISTANT).write(response)
            else:
                st.write("rephrase the query")