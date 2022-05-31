import streamlit as st
from main import *
import pandas as pd
import time
import plotly.graph_objects as go
import plotly.express as px

# step one - create containers
# containers create sections in a horizontal way and columns in a vertical way
# you can have side bars if you don't want to use the whole width of the page

# container
header = st.container()
dataset = st.container()
features = st.container()
modelTraining = st.container()

# to write sth inside of the container, we say with container and write.

with header:
    st.title('welcome to my project')
    st.text('description')
with dataset:
    st.header('Dataset')
    st.text('info about dataset')
    data = pd.read_csv('outfile_data.txt', sep=' ', header=None, names=["samples", "channel 1", "channel 2", "channel 3",
                                     "channel 4", "channel 5"])
    data = abs(data)/1000
    placeholder = st.empty()
    placeholder.line_chart(data.iloc[1:50, 1:5])
    with placeholder.container():
        for i in range(1, len(data),2):
            time.sleep(0.058)
            placeholder.line_chart(data.iloc[i:i+50, 1:5])


        # chart = st.line_chart(data.iloc[1:50, 1:])
    #
    # fig = px.line(
    #     data,  # Data Frame
    #     x="X_axis",  # Columns from the data frame
    #     y="Y_axis",
    #     title="Line frame"
    # )
    #
    # for i in range(1, 20):
    #

with features:
    st.header('features')
    st.text('info about features')


with modelTraining:
    st.header('time to train the model')
    st.text('info about training the model')