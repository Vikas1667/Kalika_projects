import pandas as pd
import pygwalker as pyg
import os, sys
import streamlit.components.v1 as components
import streamlit as st

sys.path.append('../')
import mongo_connection
from mongo_connection import insert_data


def mongo_records_poller():
    df=mongo_connection.find_mongo()
    return df

def count_plot(df,column):
    df_gb = df.groupby([column]).size().unstack(level=2)

def pygwalker():
    gwalker = pyg.walk(df,return_html=True)
    components.html(gwalker, height=1000, scrolling=True)
