import streamlit as st
from main import *
import pandas as pd
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

    chart = st.line_chart(data.iloc[1:50, 1:])

    fig = px.line(
        data,  # Data Frame
        x="X_axis",  # Columns from the data frame
        y="Y_axis",
        title="Line frame"
    )

    for i in range(1, 20):
        new_rows = data.iloc[1000*i:1000*i+1000, 1:]
        chart.add_rows(new_rows)
        last_rows = new_rows
        time.sleep(0.05)

with features:
    st.header('features')
    st.text('info about features')


with modelTraining:
    st.header('time to train the model')
    st.text('info about training the model')