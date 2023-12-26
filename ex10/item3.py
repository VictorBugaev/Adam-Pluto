#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 17:12:08 2023

@author: plutosdr
"""



import adi
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.signal import max_len_seq
import time 
import matplotlib.animation as animation



sdr = adi.Pluto('ip:192.168.2.1')
sdr.sample_rate = 1000000
sdr.tx_destroy_buffer()
 

sdr.rx_lo = 2300000000
sdr.tx_lo = 2300000000
#sdr.tx_cyclic_buffer = True
#sdr.tx_cyclic_buffer = False
sdr.tx_hardwaregain_chan0 = -5
sdr.gain_control_mode_chan0 = "slow_attack"

#fs = 1e6
fs = sdr.sample_rate
rs=100000
ns=fs//rs
 

data=max_len_seq(4)[0] 
data = np.concatenate((data,np.zeros(1)))
 
 
x_ = np.array([1,1,1,-1,-1,-1,1,-1,-1,1,-1])
b7=np.array([1,-1,1,1,1,-1,1])
ts1 =np.array([0,0,1,0,0,1,0,1,1,1,0,0,0,0,1,0,0,0,1,0,0,1,0,1,1,1])
ts2 =[0,0,1,0,1,1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1,1,0,1,1,1]
ts3 =[1,0,1,0,0,1,1,1,1,1,0,1,1,0,0,0,1,0,1,0,0,1,1,1,1,1]
ts4 =[1,1,1,0,1,1,1,1,0,0,0,1,0,0,1,0,1,1,1,0,1,1,1,1,0,0]
m=2*data-1
 
ts1t=b7
 

b = np.ones(int(ns))
 
x_IQ = np.hstack((ts1t,m))
 
#x_IQ  =  m #data transmit
N_input = len(x_IQ)

xup = np.hstack((x_IQ.reshape(N_input,1),np.zeros((N_input, int(ns-1)))))

xup= xup.flatten()
x1 = signal.lfilter(b, 1,xup) 
x=x1.astype(complex)
xt=.5*(1+x)

 
 
 

xiq=2**14*xt
#xiq=2**14*x_bb
#trdata = np.hstack((ts1,xt)).astype(complex)
triq=2**14*xt
#n_frame= len(triq)
n_frame= len(xiq)

sdr.rx_rf_bandwidth = 100000
sdr.rx_destroy_buffer()
sdr.rx_hardwaregain_chan0 = -5
sdr.rx_buffer_size =2*n_frame


plt.figure(1, figsize=(10, 10))

def send_signal(data):
    
    sdr.tx(data)

#fig = plt.figure(1, figsize=(10, 10))
#ax1 = fig.add_subplot(2, 2, 1)
#fig, (ax1, ax2) = plt.subplots(2,1)


def recv_signal(e):
    
    #ax1.clear()
    #ax2.clear()
    #ax1.ylim(-1,1)
    xrec1=sdr.rx()
    xrec = xrec1/np.mean(xrec1**2)
    #plt.clf()
    fsr=2*rs/fs
     
    xrec_a= np.abs(np.real(xrec) )
    b2,a2 = signal.butter(10,fsr,btype='lowpass')
    y1f = signal.lfilter(b2,a2,xrec_a)
     
    yf=np.convolve(xrec_a ,b)
    plt.subplot(2, 2, 2)
    plt.plot(np.abs(yf))
    #ax1.xlabel('Output of matched filter')
     
    y1f = signal.lfilter(b2,a2,yf)
    y12=signal.decimate(yf,ns)
    y=np.correlate(y12,b )
    #plt.figure(4)
    plt.subplot(2, 2, 3)
    
    plt.stem(y12)
    #plt.ylim(-0.5,0.5)
    #plt.xlabel('Output of decimator')
    ind = np.argmax(abs(y),axis=0)
    yd=y12[ind+1:ind+len(data)]
    #plt.figure(5)
    plt.subplot(2, 2, 4)
    plt.stem(yd)
    plt.show()

sdr.tx_cyclic_buffer = True
plt.subplot(2, 2, 1)
plt.plot(x_IQ)
send_signal(xiq)
#time.sleep(1)
recv_signal(1)
#ani = animation.FuncAnimation(fig, recv_signal, interval=100)
#plt.show()


 

