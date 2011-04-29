# encoding: utf-8
"""
createUVData.py

The idea here is to copy over the data from Grif-dog's HDF5 file
into a FITS IDI file.

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

import subprocess as sp
import luj

def interleave(a,b):
  command = """
  function interleave(a)
    z = table.maxn(a)/2
    c= {}
    for i=1,z do table.insert(c,a[i]) table.insert(c,a[x+i]) end  
    return c
  end
  
  po = py_obj
  
  --b = py_obj[2]
  --print(a)
  --c = a
  lo = po
  """
  
  # Luj can only handle one object at a time
  po = a+b
  
  result = luj.lua(command, python_obj=po, lua_obj='lo', lua_call='luajit')
  
  return result

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
  h5data = h5.root.xeng_raw0
  for t in range(0,10):
    for bl in range(0,100):
      
      # Open real and imaginary as seperate rows
      row_real = list(h5data[t,:,bl,0,1])
      row_imag = list(h5data[t,:,bl,0,0])
      #print row_real
  
      # Interleave real and imaginary
      real_imag = []
  
      #for i in range(0,row_real.size):
      #  real_imag.append(row_real[i])
      #  real_imag.append(row_imag[i])
      
      real_imag = interleave(row_real, row_imag)
    
      # Convert to numpy array
      real_imag = np.array(real_imag)
      uvdata.append(real_imag)
      
      if(not t%10): 
        print('. '),
      if(not bl%100): 
        print('+ %i'%bl)
    
  print len(uvdata)

  
  h5.close()

if __name__ == '__main__':
  main()

