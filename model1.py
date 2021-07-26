import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import datetime

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

#with original Data
'''
MPIO=pd.read_csv('~/Desktop/Bird_Data/MPIO_with_dist.csv')
scaler1=MinMaxScaler(feature_range=(0,1))
Xs=scaler1.fit_transform(MPIO[['temperature_average','temperature_min','temperature_max','precipitation','location-lat','location-long','dist']])
scaler2=MinMaxScaler(feature_range=(0,1))
Ys=scaler2.fit_transform(MPIO[['dist']])
'''

#with interpolated data

MPIO=pd.read_csv('~/Desktop/Bird_Data/Seris_interpolated.csv',index_col='Unnamed: 0')
MPIO.index=pd.DatetimeIndex(MPIO.index,freq='D')
MPIO['date']=pd.to_datetime(MPIO.index.date)
MPIO['lat'].interpolate(method='time',inplace=True)
MPIO['long'].interpolate(method='time',inplace=True)
print(MPIO['date'])
MPIO['day_of_year']=MPIO['date'].dt.dayofyear

print(MPIO['day_of_year'])
train_start=datetime.date(year=1991,month=8,day=23)
train_end=datetime.date(year=2017,month=4,day=1)
test_end=datetime.date(year=2020,month=3,day=30)
print(test_end)
MPIO_train=MPIO.loc[train_start:train_end,:]
MPIO_test=MPIO.loc[train_end:test_end,:]



'''
mean= MPIO_train.mean(axis=0)
std = MPIO_test.std(axis=0)
MPIO_train -=mean
MPIO_train /= std
MPIO_test -=mean
MPIO_test /= std
Xs_train=MPIO_train[['dist','temperature','tempmin','tempmax','precipitation']].to_numpy()
Xs_test=MPIO_test[['dist','temperature','tempmin','tempmax','precipitation']].to_numpy()
Ys_train=MPIO_train[['dist']].to_numpy()
Ys_test=MPIO_test[['dist']].to_numpy()
'''
feature_list=['temperature','tempmin','tempmax','precipitation']
target=['lat']
scaler1=MinMaxScaler(feature_range=(0,1))
Xs_train=scaler1.fit_transform(MPIO_train[feature_list])
Xs_test=scaler1.transform(MPIO_test[feature_list])
scaler2=MinMaxScaler(feature_range=(0,1))
Ys_train=scaler2.fit_transform(MPIO_train[target])
Ys_test=scaler2.transform(MPIO_test[target])
n_features=len(feature_list)


window=70
X_train=[]
Y_train=[]
X_test=[]
Y_test=[]
for i in range(window,len(Xs_train)):
    X_train.append(Xs_train[i-window:i,:])
    Y_train.append(Ys_train[i])
X_train ,Y_train = np.array(X_train),np.array(Y_train)

for i in range(window,len(Xs_test)):
    X_test.append(Xs_test[i-window:i,:])
    Y_test.append(Ys_test[i])
X_test ,Y_test = np.array(X_test),np.array(Y_test)

num_epochs=10
def build_model():
    model=Sequential()
    model.add(LSTM(units=50,return_sequences=True,input_shape=(X_train.shape[1],X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam',loss='mean_squared_error',metrics=['accuracy'])
    num_epochs=10
    return model
model=build_model()
def train_model(model,X,Y):
    es=EarlyStopping(monitor='loss',mode='min',verbose=1,patience=10)
    t0= time.time()
    history=model.fit(X,Y, epochs=num_epochs,batch_size=250,callbacks=[es],verbose=1)
    t1= time.time()
    print('Runtime: {:2f} s'.format(t1-t0))
    model.save('model.h5')
    epochs=np.arange(num_epochs)
    plt.figure(figsize=(8,4))
    plt.plot(epochs,history.history['loss'])
    plt.xlabel('epoch')
    plt.ylabel('tclab_loss.png')
    plt.show()
train_model(model,X_train,Y_train)


trained_model=load_model('model.h5')
Y_pred = trained_model.predict(X_test)

Y_pred=scaler2.inverse_transform(Y_pred)
Y_true=scaler2.inverse_transform(Y_test)

'''
Y_pred *= std[0]
Y_pred += mean[0]
Y_true = Y_test* std[0]
Y_true += mean
'''

#forcasting
'''
X_test_copy=Xs_test.copy()
Y_forecast=Y_pred.copy()
print(X_test_copy.shape)
for i in range(window,len(X_test_copy)):
    Xin=X_test_copy[i-window:i].reshape((1,window,n_features))
    X_test_copy[i][0]=model.predict(Xin)
    Y_forecast[i-window]=X_test_copy[i][0]
Y_forecast=scaler2.inverse_transform(Y_forecast)
'''

plt.figure(figsize=(10,6))
#fig,ax=plt.subplots(2,1,figsize=(12,12))
plt.plot(MPIO_test.index[window:],Y_pred,'r--',label='LSTM',linewidth=0.5)
plt.plot(MPIO_test.index[window:],Y_true,'k--', label='Measured',linewidth=0.5)
#plt.plot(MPIO_test.index[window:],Y_forecast,'g--', label='forecast',linewidth=0.5)
plt.suptitle('predicted {} on test data with LSTM neural network'.format(target[0]))
plt.title('used_features: {}'.format(feature_list))
plt.legend()
plt.show()

