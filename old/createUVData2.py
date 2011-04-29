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
  

  print('Opening HDF5 and FITS IFI tables')
  print('--------------------------------')  
  # Open hdf5 table
  print("opening HDF5 table...")
  h5 = tb.openFile('data.h5s')
  print("opening fits template")
  fits = pf.open('medicina.fits')
  tbl_uv_data = fits[5]
  

  print('\nReformatting HDF5 format -> FITS IDI UV_DATA')
  print('--------------------------------------------')
  # Data is stored in multidimensional array called xeng_raw0
  # time, channels, baselines, polarisation, then data=(real, imaginary) 
  (t_len, chan_len, bl_len, pol_len, ri_len) = h5.root.xeng_raw0.shape
  
  # We want to convert this into a 1D FITS IDI row
  # Loop over all times, extracting the data
  uvdata = []
  h5data = h5.root.xeng_raw0
  
  fluxes = []
  timestamps = []
  baselines = []
  
  print('Retrieving timestamps...')
  for t in range(0,t_len):
    timestamp = h5.root.timestamp0[t]
    timestamps.append(timestamp)
    
  print('Creating baseline IDs...')
  for bl in range(0,bl_len):
    # Baseline is in stupid 256*baseline1 + baseline2 format
    baseline = 256*h5.root.bl_order[bl][0] + h5.root.bl_order[bl][1]
    baselines.append(baseline)
  
  
  # This nested loop is slow. Needs speeding up  
  print('Creating multidimensional UV matrix...')
  for t in range(0,85):
    for bl in range(0,528):
      
      # Open real and imaginary as seperate rows
      row_real = h5data[t,:,bl,0,1]
      row_imag = h5data[t,:,bl,0,0]
  
      # Interleave real and imaginary
      flux = np.ndarray(shape=(row_real.size,ri_len))
  
      # This interleaves all frequencies
      for i in range(0,row_real.size):
        flux.append(row_real[i])
        flux.append(row_imag[i])
  
      # Convert to numpy array
      fluxes.append(np.array(flux))
      timestamps.append(timestamp)
      baselines.append(baseline)
      
  print('Data has been reformatted.')
  
  print('\nUpdating metadata')
  print('-----------------')    
  for i in range(0,tbl_uv_data.data.size):
    tbl_uv_data.data[i]['UU']       = 1
    tbl_uv_data.data[i]['VV']       = 1
    tbl_uv_data.data[i]['WW']       = 1
    tbl_uv_data.data[i]['DATE']     = 0
    tbl_uv_data.data[i]['TIME']     = timestamps[i]
    tbl_uv_data.data[i]['BASELINE'] = baselines[i]
    tbl_uv_data.data[i]['SOURCE']   = 1
    tbl_uv_data.data[i]['FREQID']   = 1
    tbl_uv_data.data[i]['INTTIM']   = 3
    tbl_uv_data.data[i]['WEIGHT']   = [0  in range(0,2048)]
    tbl_uv_data.data[i]['FLUX']     = fluxes[i]
  
  print "Filling array with metadata..."
  fits[5].data = tbl_uv_data.data
  fits.verify()

  print('\nWriting to file')
  print('---------------')  
  print "Finally, writing to a new file:"
  filename = 'medfits.fits'
  if(os.path.isfile(filename)):
    print('Removing existing file...')
    os.remove(filename)
  print('Writing to file...')  
  fits.writeto(filename)
  
  fits.close()
  
  h5.close()
  
  print('DONE.')

if __name__ == '__main__':
  main()

