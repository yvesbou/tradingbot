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
from sklearn.model_selection import train_test_split
import datetime

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

#with original Data

MPIO=pd.read_csv('~/Desktop/Bird_Data/MPIO_with_dist.csv',low_memory=False)

'''
MPIO["datetime"]=pd.to_datetime(MPIO['timestamp'], format="%Y-%m-%d %H:%M:%S.%f")
MPIO=MPIO.sort_values(by='datetime')
MPIO.index=pd.DatetimeIndex(MPIO['datetime'])
MPIO=MPIO.loc[~MPIO.index.duplicated(keep='first')]
individuals=MPIO['individual-local-identifier'].unique()
all_data=[]
for i in range(len(individuals)):
    individ=individuals[i]
    subset=MPIO[MPIO['individual-local-identifier']==individ]
    subset=subset.asfreq('S',method='bfill')
    subset=subset.resample('d').asfreq()
    all_data.append(subset)
print(all_data[0])
'''



MPIO['timestamp']=MPIO['timestamp'].apply(lambda x: x[:10])
MPIO["date"]=pd.to_datetime(MPIO['timestamp'], format="%Y-%m-%d")
MPIO=MPIO.sort_values(by='datetime')
MPIO.index=pd.DatetimeIndex(MPIO['date'])


individuals=np.unique(MPIO['individual-local-identifier'].values)
all_data=[]
MPIO['day_of_year']=MPIO['date'].dt.dayofyear
for i in range(len(individuals)):
    individ=individuals[i]
    subset=MPIO[MPIO['individual-local-identifier']==individ]
    subset=subset.loc[~subset.index.duplicated(keep='first')]
    subset=subset.asfreq('d',method='bfill')
    subset['temperature_average'].interpolate(method='time',inplace=True)
    subset['temperature_min'].interpolate(method='time',inplace=True)
    subset['temperature_max'].interpolate(method='time',inplace=True)
    subset['precipitation'].interpolate(method='time',inplace=True)
    #subset['day_of_year']=subset['date'].dt.dayofyear
    subset.dropna(subset=['temperature_average','temperature_min','temperature_max','precipitation',\
        'GroupZielort','GroupStartort','GroupBoth'],axis='index',inplace=True)
    if len(subset.index)>0:
        all_data.append(subset)


feature_list=['day_of_year','temperature_average','temperature_min','temperature_max','precipitation',\
        'GroupZielort','GroupStartort','GroupBoth']
target=['location-long','location-lat']
target=['StartDate']
scaler1=MinMaxScaler(feature_range=(0,1))

scaler2=MinMaxScaler(feature_range=(0,1))


window=30
X_train=[]
Y_train=[]
X_test=[]
Y_test=[]



def build_model():
    model=Sequential()
    model.add(LSTM(units=70,return_sequences=True,input_shape=(window,len(feature_list),)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=70))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam',loss='mean_squared_error',metrics=['accuracy'])
    num_epochs=1
    return model
model=build_model()

def train_model(model,X,Y):
    es=EarlyStopping(monitor='loss',mode='min',verbose=1,patience=10)
    t0= time.time()
    model.fit(X,Y, epochs=1,batch_size=10,verbose=1)   #callback=[es]
    t1= time.time()
    print('Runtime: {:2f} s'.format(t1-t0))
# train test_split
all_train_data, all_test_data=train_test_split(all_data,test_size=0.2)

#MinMax scaler fit on training and test data
scaler1.fit(MPIO[feature_list])
scaler2.fit(MPIO[target])

#train model
for k in range(12):
  for train_data in all_train_data: 
    Xs_train=scaler1.transform(train_data[feature_list])
    Ys_train=scaler2.transform(train_data[target])
    if len(Xs_train)>window:
        X_train=[]
        Y_train=[]
        for i in range(window,Xs_train.shape[0],1):
            X_train.append(Xs_train[i-window:i,:])
            Y_train.append(Ys_train[i])
        X_train ,Y_train = np.array(X_train),np.array(Y_train)
    
        train_model(model,X_train,Y_train)
model.save('model2.h5')

#test model
pred=[]
measured=[]
trained_model=load_model('model2.h5')
for test_data in all_test_data:
    Xs_test=scaler1.transform(test_data[feature_list])
    Ys_test=scaler2.transform(test_data[target])
    if len(Xs_test)>window:
        X_test=[]
        Y_test=[]
        for i in range(window,len(Xs_test)):
            X_test.append(Xs_test[i-window:i,:])
            Y_test.append(Ys_test[i])
        X_test ,Y_test = np.array(X_test),np.array(Y_test)
        Y_pred = trained_model.predict(X_test)
        Y_pred=scaler2.inverse_transform(Y_pred)
        Y_true=scaler2.inverse_transform(Y_test)
        pred.append(Y_pred)
        measured.append(Y_true)

plt.figure(figsize=(10,6))
fig,ax=plt.subplots(5,5,figsize=(12,12))
print(pred[0].shape)

#data plotting
for i in range(5):
  for j in range(5):
    ax[i,j].plot(pred[i*5+j][window:,0],pred[i*5+j][window:,1],'r--',label='LSTM',linewidth=0.5)
    ax[i,j].plot(measured[i*5+j][window:,0],measured[i*5+j][window:,1],'k--', label='Measured',linewidth=0.5)
#plt.legend()
#plt.tick_params(labelcolor='none',top='off',bottom='off', left='off',right='off')
#plt.xlabel('longitude')
#plt.ylabel('lattitude')
ax[0,2].set_title('predicted longitude and latitude on test data')
plt.show()


