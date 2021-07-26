
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 19:35:18 2020

@author: christophboomer
"""
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from botapi import BotApi
start=datetime.datetime(2010,1,1)
start=datetime.timestamp(start)
end=datetime.datetime(2020,8,19)
end=datetime.timestamp(end)
api=BotApi(platform='poloniex')
api.chartToCsv(period=60,pair='USDT_BTC',start=start,end=end)


print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

#inspiration

# run multiple models the same time with a single gpu using the code below
gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))


# using TensorBoard
from tensorflow.keras.callbacks import TensorBoard

tensorboard = TensorBoard(logdir='logs/{}'.format(Name_of_Model))
...
# remember callbacks wants a list of the callbacks options
model.fit(X, y, batch_size=.., epochs=.., validation_split=.., callbacks=[tensorboard])

