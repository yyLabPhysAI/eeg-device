import threading
import time

import altair
import numpy as np
from IPython.core.display_functions import display
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from queue import Queue
from threading import Thread
from pathlib import Path

from numpy import NaN
from streamlit import caching

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

from streamlit.scriptrunner import add_script_run_ctx


class Client():
    def __init__(self, datatype, q, q_for_ploting):
        self.params = BrainFlowInputParams()
        self.params.serial_port = 'com3'
        self.params.board_id = 0
        self.board = BoardShim(0, self.params)
        self.datatype = datatype
        self.file_path = None
        self.fake_matrix = None
        self.df = None
        self.fake_df = None
        self.times_to_go_over = 0
        self.q = q
        self.q_for_ploting = q_for_ploting

    def start_print(self):
        t2 = Thread(target=Client.print_data, args=(self,))
        t2.start()

    def print_data(self):
        while True:
            time.sleep(5)
            # return 1
            temporary_df = pd.DataFrame()
            for i in range(self.q.qsize()):
                temporary_df = pd.concat([temporary_df, self.q.get()])
                self.q.task_done()

    def start_collect(self, dataype):
        t1 = Thread(target=Client.collect_data, args=(self, dataype))
        t1.start()

    def collect_data(self, datatype):
        if datatype == 'real':
            start_real = Real(self, self.q, self.q_for_ploting)
            start_real.start_stream()
            while True:
                time.sleep(0.2)
                d = start_real.read_data()
                A = pd.DataFrame(d[0:6, :])
                A = A.transpose()
                A.columns = ["samples", "channel 1", "channel 2", "channel 3",
                             "channel 4", "channel 5"]
                B = A
                self.q.put(A)
                self.q_for_ploting.put(B)

        else:
            start_fake = Fake(self, self.q, self.q_for_ploting)
            start_fake.choose_file()
            data = start_fake.read_file()
            times = start_fake.passes_calc()
            for i in range(times):
                time.sleep(1 / 64)
                temp_df = data[i * 4:i * 4 + 4]
                self.q.put(temp_df)
                self.q_for_ploting.put(temp_df)


class Real(Client):
    def start_stream(self):
        self.board.prepare_session()
        self.board.start_stream()

    def read_data(self):
        data = self.board.get_board_data()
        return data

    def stop_stream(self):
        self.board.stop_stream()
        self.board.release_session()


class Fake(Client):
    def choose_file(self):
        root = tk.Tk()
        root.withdraw()
        self.file_path = Path(filedialog.askopenfilename())
        return self.file_path

    def read_file(self):
        self.df = pd.read_csv(self.file_path, sep=" ", header=None,
                              names=["samples", "channel 1", "channel 2", "channel 3",
                                     "channel 4", "channel 5"])
        return self.df

    def passes_calc(self):
        rows = len(self.df.index)
        self.times_to_go_over = int(np.floor(rows / 4))
        return self.times_to_go_over


def streaming_app():
    datatype = 'real'
    q = Queue()
    q_for_plotting = Queue()
    c = Client(datatype, q, q_for_plotting)

    st.set_page_config(page_title='Epileptic seizures detector/predictor', page_icon='😊')
    st.image(r'BioMedTechnionLogoEngColorW2-NEW.png', width=500)
    st.title("Epileptic seizures detector/predictor")

    # hide the menu button

    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    # condense the layout - remove the padding between components of website

    padding = 0
    st.markdown(f""" <style>
        .reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {padding}rem;
            padding-left: {padding}rem;
            padding-bottom: {padding}rem;
        }} </style> """, unsafe_allow_html=True)

    # Using object notation
    add_selectbox = st.sidebar.selectbox(
        "Who would you like to contact in case of an emergency?",
        ("Contact1", "Contact2", "Contact3")
    )
    col1, col2, col3 = st.columns((10, 4, 1))
    col1.header("Live Data")
    col2.header("Result")
    col2.text('No sign of seizure')
    # col2.image("result.jpg", width=100)

    c.start_collect(datatype)
    c.start_print()
    q.join()
    placeholder = col1.empty()
    placeholder_2 = col1.empty()
    placeholder_3 = col1.empty()
    data = pd.DataFrame()
    time.sleep(2.5)

    with st.sidebar:
        add_radio = st.radio(
            "are you wearing the deivce?",
            ("YES", "NO")
        )
    # lines = altair.Chart(data).mark_line().encode(x=altair.X('1:T'))
    # # with placeholder.container():
    # line_plot = st.altair_chart(lines)
    # while True:
    #     data = abs(pd.concat([data, q_for_plotting.get() / 1000]))
    #     step_df = data.iloc[-500:, 1]
    #     lines = plot_animation(step_df)
    #     line_plot = line_plot.altair_chart(lines)
    #     time.sleep(0.1)
    with placeholder.container():
        while True:
            fig, ax = plt.subplots(3)
            data = abs(pd.concat([data, q_for_plotting.get() / 1000],ignore_index=True))
            ax[0].plot(data.iloc[-500:, 1])
            # ax[0].set_title('EEG 1')
            ax[0].set_xticks([])
            ax[0].set_yticks([])
            ax[1].plot(data.iloc[-500:, 2])
            # ax[1].set_title('\n EEG 2')
            ax[1].set_xticks([])
            ax[1].set_yticks([])
            ax[2].plot(data.iloc[-500:, 3])
            ax[2].set_xticks([])
            ax[2].set_yticks([])
            # ax[2].set_title('\n EEG 3')
            plt.draw()
            placeholder.plotly_chart(fig)
            q_for_plotting.task_done()
            time.sleep(0.01)

    # with placeholder.container():
    #     fig = plt.figure()
    #     while True:
    #         test = [data,q_for_plotting.get() / 1000]
    #         data = abs(pd.concat[test,data])
    #         data = data.iloc[-500:, 1:4]
    #         placeholder.pyplot(fig)
    #         q_for_plotting.task_done()
    #         time.sleep(0.01)

    # with placeholder.container():
    #     while True:
    #         data = abs(pd.concat([data, q_for_plotting.get() / 1000],ignore_index=True))
    #         chart = (
    #             altair.Chart(
    #                 data=pd.DataFrame(data.iloc[-500:, :]),
    #                 title="EEG Channel 1",
    #             )
    #                 .mark_line()
    #                 .encode(
    #                 x=altair.X("samples", axis=altair.Axis(title="samples")),
    #                 y=altair.Y("channel 1", axis=altair.Axis(title="channel 1")),
    #             )
    #         )
    #         placeholder = placeholder.altair_chart(chart)
    #         chart = (
    #             altair.Chart(
    #                 data=pd.DataFrame(data.iloc[-500:, :]),
    #                 title="EEG Channel 1",
    #             )
    #                 .mark_line()
    #                 .encode(
    #                 x=altair.X("samples", axis=altair.Axis(title="samples")),
    #                 y=altair.Y("channel 2", axis=altair.Axis(title="channel 2")),
    #             )
    #         )
    #         placeholder_2 = placeholder_2.altair_chart(chart)
    #         chart = (
    #             altair.Chart(
    #                 data=pd.DataFrame(data.iloc[-500:, :]),
    #                 title="EEG Channel 1",
    #             )
    #                 .mark_line()
    #                 .encode(
    #                 x=altair.X("samples", axis=altair.Axis(title="samples")),
    #                 y=altair.Y("channel 3", axis=altair.Axis(title="channel 3")),
    #             )
    #         )
    #         placeholder_3 = placeholder_3.altair_chart(chart)
    #         q_for_plotting.task_done()
    #         time.sleep(0.01)
    # with placeholder.container():
    #
    #     while True:
    #
    #         data = abs(pd.concat([data, q_for_plotting.get() / 1000]))
    #         placeholder.line_chart(data.iloc[-256:, 1:4])
    #
    #         q_for_plotting.task_done()
    #         time.sleep(0.01)


streaming_app()
