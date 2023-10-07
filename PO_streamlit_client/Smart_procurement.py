# from transformers import T5Tokenizer, T5ForConditionalGeneration
import streamlit as st
import sys,os
import pandas as pd
import streamlit as st
import altair as alt
import base64
import matplotlib.pyplot as pltt
print(os.getcwd())
# V:\ML_projects\github_projects\Purchase-Order-Application\PO_streamlit_client
import mongo_test

from transformers import pipeline

from PIL import Image

def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

my_logo = add_logo(logo_path="imgs/Kalika logo.png", width=300, height=60)
st.image(my_logo)
st.title("SMART Procurement")


tab1, tab2 = st.tabs(["Buyer Analysis", "Generate item description"])



with tab2:
    generator = pipeline('text-generation', model = 'gpt2')
    text_inp=st.text_input('Enter the text')
    if text_inp:
        text_out=generator(text_inp, max_length = 200, num_return_sequences=3)
        for i in text_out:
            st.write(i)
