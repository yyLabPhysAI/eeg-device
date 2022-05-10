import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from queue import Queue
from threading import Thread


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
            m = start_real.read_data()
            for i in range(10):
                time.sleep(1)
                d = start_real.read_data()
                m = np.append(m, d, axis=1)
            return m
        else:
            start_fake = Fake(self)
            self.file_path = start_fake.choose_file()
            self.fake_matrix = start_fake.read_file()
            self.times_to_go_over=start_fake.passes_calc()
            return self.fake_matrix, self.times_to_go_over


class Real(Client):
    pass

    def collect_data_live(self):
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


def the_data(datatype,out_q):
    if datatype == 'real':
        start_real = Real()
        start_real.collect_data_live()
        m = start_real.read_data()
        for i in range(120):
            time.sleep(1)
            d = start_real.read_data()
            m = np.append(m, d, axis=1)
        start_real.stop_stream()
        return m
    if datatype == 'fake':
        fake_matrix = Client(datatype)
        the_fake_matrix, passes = fake_matrix.collect_data(datatype)
        for i in range(passes):
            time.sleep(1)
            temp_df = the_fake_matrix[i * 256:i * 256+256]
            out_q.put(temp_df)


def testing_queue(in_q):
    while True:
        time.sleep(5)
        data = in_q.get()
        print(data)
        in_q.task_done()


datatype = 'fake'
q = Queue()
t1 = Thread(target=the_data, args=(datatype, q))
t2 = Thread(target=testing_queue, args=(q, ))
t1.start()
t2.start()
q.join()

# df = pd.DataFrame(data=transposed)
# print(df.shape)
# df.to_csv('outfile.txt', sep=' ', header=False, index=False)


# params = BrainFlowInputParams()
# params.serial_port = 'com3'
# params.board_id = 0
# board = BoardShim(0,params)

# test = Real()
# board = test.collect_data()
# # time.sleep(1)
# matrix = board.get_board_data()
# r = 2
# for i in range(r):
#     time.sleep(1)
#     data = board.get_board_data()
#     matrix = np.append(matrix, data, axis=1)
# board.stop_stream()
# board.release_session()


# matrix = c.collec_data(datatype)
# x = matrix.shape[1] - 1
# frequency = BoardShim.get_sampling_rate(params.board_id)
# print(frequency)
# t = np.linspace(0, 60, num=x)
# test = (matrix[2, 1:]) / 1000000
# eegmatrix = matrix[0:6, :]
# transposed = eegmatrix.T
# plt.plot(t, test)
#
# plt.show()
