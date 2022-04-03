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
params = BrainFlowInputParams()
params.serial_port = 'com3'
params.board_id = 0
board = BoardShim(0,params)
board.prepare_session()
board.start_stream()
# time.sleep(1)
matrix = board.get_board_data()
r = 2
for i in range(r):
    time.sleep(1)
    data = board.get_board_data()
    matrix = np.append(matrix, data, axis=1)
    r += 1
board.stop_stream()
board.release_session()
x = matrix.shape[1]-1
frequency = BoardShim.get_sampling_rate(params.board_id)
print(frequency)
t = np.linspace(0, r, num=x)
test = (matrix[7, 1:])/1000000
plt.plot(t, test)

plt.show()