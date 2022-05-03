import argparse
import logging
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import mne
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from matplotlib import pyplot as plt
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
import pandas as pd
import tkinter as tk
from tkinter import filedialog
class Client():
    def __init__(self,datatype):
        self.params = BrainFlowInputParams()
        self.params.serial_port = 'com3'
        self.params.board_id = 0
        self.board = BoardShim(0, self.params)
        self.datatype = datatype
        self.file_path = None
    #     self.matrix = matrix
    #
    # def board_shim(self):
    #     if self.datatype == 'real':
    #         self.data = Real.collect_data()
    #         return self.data
    #     else:
    #         print('hello')

    def collec_data(self,datatype):
        if datatype == 'real':
            start_real = Real(self)
            start_real.collect_data()
            m = start_real.read_data()
            for i in range(10):
                time.sleep(1)
                d = start_real.read_data()
                m = np.append(m, d, axis=1)
            # start_real.stop_stream()
            return m
        else:
            start_fake = Fake(self)
            file =start_fake.choose_file()

class Real(Client):
    pass

    def collect_data(self):
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

def the_data(datatype):
    if datatype == 'real':
        start_real = Real()
        start_real.collect_data()
        m = start_real.read_data()
        for i in range(120):
            time.sleep(1)
            d = start_real.read_data()
            m = np.append(m, d, axis=1)
        start_real.stop_stream()
        return m

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
datatype = 'fake'
c = Client(datatype)
matrix = c.collec_data(datatype)
x = matrix.shape[1] - 1
# frequency = BoardShim.get_sampling_rate(params.board_id)
# print(frequency)
t = np.linspace(0, 60, num=x)
test = (matrix[2, 1:]) / 1000000
# eegmatrix = matrix[0:6, :]
# transposed = eegmatrix.T
plt.plot(t, test)
# df = pd.DataFrame(data=transposed)
#
# print(df.shape)
# df.to_csv('outfile.txt', sep=' ', header=False, index=False)
plt.show()
