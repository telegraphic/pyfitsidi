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
import pyfits as pf, numpy as np, tables as tb, cPickle as pkl

def main():
  

  
  # Open hdf5 table
  h5 = tb.openFile('data.h5s')
  fits = pf.open('medicina.fits')
  tbl_uv_data = fits[5]
  
  for i in range(0,tbl_uv_data.data.size):
    tbl_uv_data.data[i]['UU']       = 1
    tbl_uv_data.data[i]['VV']       = 1
    tbl_uv_data.data[i]['WW']       = 1
    tbl_uv_data.data[i]['DATE']     = 0
    tbl_uv_data.data[i]['TIME']     = 0
    tbl_uv_data.data[i]['BASELINE'] = 1
    tbl_uv_data.data[i]['SOURCE']   = 1
    tbl_uv_data.data[i]['FREQID']   = 1
    tbl_uv_data.data[i]['INTTIM']   = 3
    tbl_uv_data.data[i]['WEIGHT']   = [0  in range(0,2048)]
  
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
      row_real = h5data[t,:,bl,0,1]
      row_imag = h5data[t,:,bl,0,0]
  
      # Interleave real and imaginary
      flux = []
  
      for i in range(0,row_real.size):
        flux.append(row_real[i])
        flux.append(row_imag[i])
  
      # Convert to numpy array
      # flux = np.array(flux)
      uvdata.append([UU,VV,WW,DATE,TIME,BASELINE,SOURCE,FREQID,INTTIM,WEIGHT,flux])
      
      if(not t%10):   print('. '),
      if(not bl%100): print('+ %i'%bl)
   
  print len(uvdata)
  print uvdata[0]
  
  h5.close()

if __name__ == '__main__':
  main()

