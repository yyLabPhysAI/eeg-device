import threading
import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from queue import Queue
from threading import Thread
import streamlit as st
from streamlit.scriptrunner import add_script_run_ctx



class Client():
    def __init__(self, datatype):
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

    def collect_data(self, datatype):
        if datatype == 'real':
            start_real = Real(self)
            start_real.collect_data_live()

        else:
            start_fake = Fake(self)
            self.file_path = start_fake.choose_file()
            self.fake_matrix = start_fake.read_file()
            self.times_to_go_over = start_fake.passes_calc()
            return self.fake_matrix, self.times_to_go_over

    def real_data_collection(self):
        start_real = Real(self)
        m = start_real.read_data()
        for i in range(10):
            time.sleep(1)
            d = start_real.read_data()
            m = np.append(m, d, axis=1)
        return m


class Real(Client):
    pass

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
        self.file_path = filedialog.askopenfilename()
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


def the_data(datatype, out_q):
    if datatype == 'real':
        start_real = Real(datatype)
        start_real.start_stream()
        counter = 0
        time.sleep(1)
        while counter < 600:
            d = start_real.read_data()
            A = pd.DataFrame(d)
            A = A.transpose()
            out_q.put(A)
            counter += 1

    if datatype == 'fake':
        fake_matrix = Client(datatype)
        the_fake_matrix, passes = fake_matrix.collect_data(datatype)
        time.sleep(1)
        for i in range(passes):
            temp_df = the_fake_matrix[i * 256:i * 256 + 256]
            out_q.put(temp_df)


def get_all_queue_result(queue):
    result_list = []
    while not queue.empty():
        result_list.append(queue.get())
    return result_list


def testing_queue(in_q, all_data):
    while True:
        time.sleep(5)
        temporary_df = pd.DataFrame()
        for i in range(in_q.qsize()):
            temporary_df = pd.concat([temporary_df, in_q.get()])
        all_data = pd.concat([all_data, temporary_df], axis=0)
        in_q.task_done()


def streamlitapp(q):
    header = st.container()
    dataset = st.container()
    features = st.container()
    modelTraining = st.container()

    with header:
        st.title('welcome to my project')
        st.text('description')
    with features:
        st.header('features')
        st.text('info about features')
    with dataset:
        st.header('Dataset')
        st.text('info about dataset')
        # data =
        data = abs(data) / 1000
        placeholder = st.empty()
        placeholder.line_chart(data.iloc[1:50, 1:5])
        with placeholder.container():
            for i in range(1, len(data), 2):
                time.sleep(0.058)
                placeholder.line_chart(data.iloc[i:i + 50, 1:5])
    with modelTraining:
        st.header('time to train the model')
        st.text('info about training the model')


def main():
    datatype = 'fake'
    q = Queue()
    all_data = pd.DataFrame()
    t1 = Thread(target=the_data, args=(datatype, q))
    t2 = Thread(target=testing_queue, args=(q, all_data))
    t1.start()
    t2.start()
    t3 = Thread(target=streamlitapp, args=(q,))
    add_script_run_ctx(t3)
    t3.start()
    q.join()


if __name__ == '__main__':
    main()

