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

The actual data matrix is stored per row as a multidimensional matrix
with the following mandatory axes:
COMPLEX     Real, imaginary, weight
STOKES      Stokes parameter
FREQ        Frequency (spectral channel)
RA          Right ascension of the phase center
DEC         Declination of the phase center

Created by Danny Price on 2011-04-21.
Copyright (c) 2011 The University of Oxford. All rights reserved.
"""

import sys, os
import pyfits as pf, numpy as np, tables as tb, cPickle as pkl

def main():
  

  print('Opening HDF5 and FITS IDI tables')
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
  h5data = h5.root.xeng_raw0
  
  # We want to convert this into a 1D FITS IDI row
  # So we need to transpose baselines and channels
  # and also, real and imaginary, as the SPEAD format makes the inner
  # dimension [imag,real], and we want [real,imag]
  print('Creating new uv_matrix...')
  ra_len, dec_len = 1, 1
  uvmatrix = np.ndarray(shape=(ra_len, dec_len, t_len, bl_len, chan_len, pol_len, ri_len))
  uvmatrix[:] = 0 # For some reason it fills it up with absolute crap by default

  # This is really slow...
  print('Transposing HDF5 (baselines <-> channels), and (imag <-> real)...')
  for bl in range(0,bl_len):
    uvmatrix[0,0,:,bl,:,:,0] = h5data[:,:,bl,:,1]
    uvmatrix[0,0,:,bl,:,:,1] = h5data[:,:,bl,:,0]
    if not bl%10:
      print('Transposing baseline %i/%i'%((bl+1),bl_len)) 
  
  fluxes = []
  timestamps = []
  baselines = []
  

  for t in range(0,t_len):
    print('Retrieving timestamps...')
    timestamp = h5.root.timestamp0[t]
    timestamps.append(timestamp)
    
  for bl in range(0,bl_len):
    print('Creating baseline IDs...')
    # Baseline is in stupid 256*baseline1 + baseline2 format
    baseline = 256*h5.root.bl_order[bl][0] + h5.root.bl_order[bl][1]
    baselines.append(baseline)

"""

      # Convert to numpy array
      fluxes.append(
        np.array(ra, dec, freq, stokes, cplex)
        )
      
      
      
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
  """

if __name__ == '__main__':
  main()

