import transformer
from transformers import pipeline
import streamlit as st

def text_generator():
    generator = pipeline('text-generation', model = 'gpt2')
    text_inp=st.text_input('Enter the text')
    if text_inp:
        text_out=generator(text_inp, max_length = 200, num_return_sequences=3)
        for i in text_out:
            st.write(i)
