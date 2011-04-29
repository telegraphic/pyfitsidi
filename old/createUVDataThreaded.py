# encoding: utf-8
"""
createUVDataThreaded.py

The idea here is to copy over the data from Grif-dog's HDF5 file
into a FITS IDI file.

BUT NOW WE DO IT WITH THREADS

UV_DATA table data
--------------------
UU           Baseline vector U coordinate 
VV           Baseline vector V coordinate
WW           Baseline vector W coordinate
DATE         UTC Julian day value for time 00:00:00 
             on the day of the observation
TIME         Fraction of Julian day from UTC time 00:00:00 to 
             UTC time of observation on day of observation.
BASELINE     Antenna baseline pair ID.
FILTER       VLBA filter ID
SOURCE       Data source ID
FREQID       Data frequency setup ID
INTTIM       Data integration time
WEIGHT       Data weights (one element for each freq channel)
GATEID       VLBA gate ID
FLUX         UV visibility data matrix

Created by Danny Price on 2011-04-21.
Copyright (c) 2011 The University of Oxford. All rights reserved.
"""

import sys, os
import pyfits as pf, numpy as np, tables as tb

import threading
from Queue import Queue

class Interleaver(threading.Thread):
  def __init__(self, row_real, row_imag):
    self.row_real = row_real
    self.row_imag = row_imag
    self.result = None
    threading.Thread.__init__(self)
  
  def get_result(self):
    return self.result
  
  def run(self):
    # Interleave real and imaginary
    real_imag =[]

    for i in range(0,self.row_real.size):
      real_imag.append(self.row_real[i])
      real_imag.append(self.row_imag[i])
      
    # Convert to numpy array
    self.result = np.array(real_imag)

   
def threadmake(q, row_real, row_imag):
    # Start a thread to do the interleaving
    thread = Interleaver(row_real, row_imag)
    thread.start()
    q.put(thread, True)

def threadread(q, data):
    thread = q.get(True)
    thread.join()
    data.append(thread.get_result())

def main():
  
  # Create record array  UU       VV       WW       DATE     TIME     BASELINE
  x = np.zeros(1, dtype='float32, float32, float32, float64, float64, int32,  \
      int32, int32, float32, 2048float32,  2048float32')
  #   SOURCE FREQID INTTIM   WEIGHT        FLUX   
  
  
  
  # Open hdf5 table
  h5 = tb.openFile('data.h5s')
  
  # Data is stored in multidimensional array called xeng_raw0
  # time, channels, baselines, polarisation, then data=(real, imaginary) 
  (t_len, chan_len, bl_len, pol_len, ri_len) = h5.root.xeng_raw0.shape
  
  # We want to convert this into a 1D FITS IDI row
  # Loop over all times, extracting the data
  uvdata = []
  
  q = Queue(4)
  data = []
  
  for bl in range(0,bl_len):
    for t in range(0,t_len):
      # Open real and imaginary as seperate rows
      row_real = h5.root.xeng_raw0[t,:,bl,0,1]
      row_imag = h5.root.xeng_raw0[t,:,bl,0,0]
      
      make_thread = threading.Thread(target=threadmake, args=(q, row_real, row_imag))
      read_thread = threading.Thread(target=threadread, args=(q,data))
      make_thread.start()
      read_thread.start()
      make_thread.join()
      read_thread.join()

      if(not bl%100): print('+ %i'%bl)
    
  print len(uvdata)
  

  
  h5.close()

if __name__ == '__main__':
  main()

