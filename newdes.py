import threading
import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from queue import Queue
from threading import Thread
from pathlib import Path
from streamlit import caching

import streamlit as st
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
        t2 = Thread(target=Client.print_data, args=(self, ))
        t2.start()
    def print_data(self):
        while True:
            time.sleep(5)
            temporary_df = pd.DataFrame()
            for i in range(self.q.qsize()):
                temporary_df = pd.concat([temporary_df, self.q.get()])
                self.q.task_done()
    def start_collect(self, dataype):
        t1 = Thread(target=Client.collect_data, args=(self,dataype ))
        t1.start()
    def collect_data(self, datatype):
        if datatype == 'real':
            start_real = Real(self, self.q, self.q_for_ploting)
            start_real.start_stream()
            while True:
                time.sleep(1)
                d = start_real.read_data()
                A = pd.DataFrame(d)
                A = A.transpose()
                B = A
                self.q.put(A)
                self.q_for_ploting.put(B)

        else:
            start_fake = Fake(self, self.q, self.q_for_ploting)
            start_fake.choose_file()
            data = start_fake.read_file()
            times = start_fake.passes_calc()
            for i in range(times):
                time.sleep(1)
                temp_df = data[i * 256:i * 256 + 256]
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
        self.times_to_go_over = int(np.floor(rows / 256))
        return self.times_to_go_over


def streaming_app_for_mais_lano_n2rt_rase():
    datatype = 'fake'
    header = st.container()
    dataset = st.container()
    q = Queue()
    q_for_plotting = Queue()
    c = Client(datatype, q, q_for_plotting)
    with header:
        st.title('welcome to my project')
        st.text('description')
    with dataset:
        st.header('Dataset')
        st.text('info about dataset')
    c.start_collect(datatype)
    c.start_print()
    q.join()
    placeholder = st.empty()

    while True:
        data = pd.DataFrame()
        with placeholder.container():
            data = abs(pd.concat([data, q_for_plotting.get()/1000]))
            placeholder.line_chart(data.iloc[:, 1:4])
            time.sleep(1)
streaming_app_for_mais_lano_n2rt_rase()