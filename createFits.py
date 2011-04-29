# encoding: utf-8
"""
createFits.py
=============

Creates a fits file out of a template. Made for Medicina X engine FitsIDI
Based off the LWA Fits IDI, because it's well documented! Many of the
notes in this file are copied over from this document.

Created by Danny Price on 2011-04-20.
Copyright (c) 2011 The University of Oxford. All rights reserved.

"""

import sys, os
import pyfits as pf, numpy as np,  tables as tb

# FITS IDI python module imports
from pyFitsidi import *


def config_antenna(tbl):
  """
  Configures the antenna table with some default values
  """

  antenna = tbl.data
  for i in range(0,tbl.data.size):
    
    antenna[i]['ANNAME']      = 'MED_%i'%i
    antenna[i]['ANTENNA_NO']  = i
    antenna[i]['ARRAY']       = 1
    antenna[i]['FREQID']      = 1
    antenna[i]['NO_LEVELS']   = 12
    antenna[i]['POLTYA']      = 'R'
    antenna[i]['POLTYB']      = 'R'
    antenna[i]['POLAA']       = 0
    antenna[i]['POLAB']       = 0
    
    
  tbl.data = antenna

  return tbl

def config_source(tbl):
  """
  Configures the source table with some default values
  """
  
  sourcename = 'CygnusA'
  print('Source is: %s'%sourcename)
  
  source = tbl.data[0]
  
  source['SOURCE_ID'] = 1
  source['SOURCE']    = sourcename
  source['VELDEF']    = 'RADIO'
  source['VELTYP']    = 'GEOCENTR'
  source['FREQID']    = 1
  source['RAEPO']     = 299.8667
  source['DECEPO']    = 40.7339
  source['EQUINOX']   = 'J2000'
  
  # Things I'm just making up
  source['IFLUX']    = 0
  source['QFLUX']    = 0
  source['UFLUX']    = 0
  source['VFLUX']    = 0
  source['ALPHA']    = 0
  source['FREQOFF']  = 0
  
  tbl.data[0] = source
  
  return tbl

def config_frequency(tbl):
  """
  Configures the frequency table with some default values
  """

  frequency = tbl.data[0]

  frequency['FREQID']         = 1
  frequency['BANDFREQ']       = 0
  frequency['CH_WIDTH']       = 20.0/1024.0 * 10**6
  frequency['TOTAL_BANDWIDTH']= 20*10**6
  frequency['SIDEBAND']       = 1

  tbl.data[0] = frequency

  return tbl  

def config_array_geometry(tbl):
  """
  Configures the array_geometry table with Medicina values
  """
  
  geometry = tbl.data

  # We are at Medicina, Italy
  (latitude, longitude, elevation) = ('44:31:24.88', '11:38:45.56', 28)
  
  # Antenna positions are relative to the array centre
  
  # X-Y-Z in nanoseconds (re-ordered by hand)
  xyz_ns = np.array([
         [ -11.69,  -26.68,   11.89],  #0
         [ -11.69,  -46.29,   11.89],  #1
         [ -11.69,  -65.90,   11.89],  #2
         [ -11.69,  -85.50,   11.89],  #3
         [ -35.08,  -26.68,   35.67],  #4
         [ -35.08,  -46.29,   35.67],  #5
         [ -35.08,  -65.90,   35.67],  #6
         [ -35.08,  -85.50,   35.67],  #7
         [ -58.47,  -26.68,   59.45],  #8
         [ -58.47,  -46.29,   59.45],  #9
         [ -58.47,  -65.90,   59.45],  #10
         [ -58.47,  -85.50,   59.45],  #11
         [ -81.86,  -26.68,   83.23],  #12
         [ -81.86,  -46.29,   83.23],  #13
         [ -81.86,  -65.90,   83.23],  #14
         [ -81.86,  -85.50,   83.23],  #15
         [-105.25,  -26.68,  107.01],  #16
         [-105.25,  -46.29,  107.01],  #17
         [-105.25,  -65.90,  107.01],  #18
         [-105.25,  -85.50,  107.01],  #19
         [-128.64,  -26.68,  130.80],  #20
         [-128.64,  -46.29,  130.80],  #21
         [-128.64,  -65.90,  130.80],  #22
         [-128.64,  -85.50,  130.80],  #23
         [-152.03,  -26.68,  154.58],  #24
         [-152.03,  -46.29,  154.58],  #25
         [-152.03,  -65.90,  154.58],  #26
         [-152.03,  -85.50,  154.58],  #27
         [-175.42,  -26.68,  178.36],  #28
         [-175.42,  -46.29,  178.36],  #29
         [-175.42,  -65.90,  178.36],  #30
         [-175.42,  -85.50,  178.36]],  #31
         dtype = 'float32')
  
  # X-Y-Z in metres
  xyz_m = xyz_ns * 10**-9 * 299792458

  # The antenna numbering jumps about a bit
  ant_num = np.array([i for i in range(0,32)])
  
  for i in range(0,tbl.data.size):
    geometry[i]['ANNAME']  = 'MED_%i'%ant_num[i]
    geometry[i]['STABXYZ'] = xyz_ns[i]
    geometry[i]['DERXYZ']  =  0
    #geometry[i]['ORBPARM'] = 0
    geometry[i]['NOSTA']   = ant_num[i]
    geometry[i]['MNTSTA']  = 1 
    # NOTE: Aperture arrays are given code 6, but not supported by CASA
    geometry[i]['STAXOF']  = np.array([0,0,0])
    geometry[i]['DIAMETER'] = 0

  tbl.data = geometry

  return tbl

def config_system_temperature(tbl):
  """
  Configures the system_temperature table with values for Medicina
  """
    
  system_temp = tbl.data
  
  for i in range(0, tbl.data.size): 
    system_temp[i]['TIME'] = 0
    system_temp[i]['TIME_INTERVAL'] = 365 
    system_temp[i]['SOURCE_ID']  = 1 
    system_temp[i]['ANTENNA_NO'] = i 
    system_temp[i]['ARRAY'] = 1
    system_temp[i]['FREQID'] = 1
    system_temp[i]['TSYS_1'] = 87 
    system_temp[i]['TANT_1'] = 47
  
  tbl.data = system_temp
  
  return tbl 
     
def main():
  """
  Generate a blank FITS IDI file for use in Medicina BEST-2
  32 element array.
  """
  
  # What are the filenames for our datasets?
  hdffile  = '../hdf5/corr.2455676.70269.h5c.cyg'
  fitsfile = 'corr.2455676.70269.fits'
  
  # Make a new blank FITS HDU
  hdu = make_primary()
  
  # Go through and generate required tables
  tbl_array_geometry = make_array_geometry(num_rows=32)
  tbl_array_geometry = config_array_geometry(tbl_array_geometry)
  #print tbl_array_geometry.header.ascardlist()
  
  tbl_frequency = make_frequency(num_rows=1)
  tbl_frequency = config_frequency(tbl_frequency)
  #print tbl_frequency.header.ascardlist()
  print('\n')

  print('Creating SOURCE')
  print('------------------------------------')
  tbl_source = make_source(num_rows=1)
  tbl_source = config_source(tbl_source)
  #print tbl_source.header.ascardlist()
  print('\n')

  print('Creating ANTENNA')
  print('------------------------------------')
  tbl_antenna = make_antenna(num_rows=32)
  tbl_antenna = config_antenna(tbl_antenna)
  #print tbl_antenna.header.ascardlist()
  print('\n')

  # FLAG is optional. Skip for now
  # print('Creating FLAG')
  # print('------------------------------------')
  # tbl_flag = make_flag()
  # print tbl_flag.header.ascardlist()
  # print('\n')
  
  # GAIN_CURVE is optional. Skip for now
  # print('Creating GAIN_CURVE')
  # print('------------------------------------')
  # tbl_gain_curve = make_gain_curve()
  # print tbl_gain_curve.header.ascardlist()
  # print('\n')  
  
  # INTERFEROMETER_MODEL is optional table, we are not including it.
  # print('Creating INTERFEROMETER_MODEL')
  # print('------------------------------------')
  # tbl_interferometer_model = make_interferometer_model()
  # print tbl_interferometer_model.header.ascardlist()
  # print('\n')
  
  # PHASE-CAL is optional. Skip for now.
  # print('Creating PHASE-CAL')
  # print('------------------------------------')
  # tbl_phase_cal = make_phase_cal()
  # print tbl_phase_cal.header.ascardlist()
  # print('\n')

  # SYSTEM_TEMPERATURE table is optional
  print('Creating SYSTEM_TEMPERATURE')
  print('------------------------------------')
  tbl_system_temperature = make_system_temperature(num_rows=32)
  tbl_system_temperature = config_system_temperature(tbl_system_temperature)
  # print tbl_system_temperature.header.ascardlist()
  print('\n')
  
  # Bandpass is optional too
  # print('Creating BANDPASS')
  # print('------------------------------------')
  # tbl_bandpass = make_bandpass()
  # print tbl_bandpass.header.ascardlist()
  # print('\n')
  
  # UV_DATA data - MANDATORY
  print('Creating UV_DATA')
  print('------------------------------------')
  # Open hdf5 table
  print('Opening HDF5 table %s'%hdffile)
  h5 = tb.openFile(hdffile)
  
  # Data is stored in multidimensional array called xeng_raw0
  # time, channels, baselines, polarisation, then data=(real, imaginary) 
  (t_len, chan_len, bl_len, pol_len, ri_len) = h5.root.xeng_raw0.shape
  print('Data dimensions: %i dumps, %i chans, %i baselines, %i pols, %i data (real/imag)'\
  %(t_len, chan_len, bl_len, pol_len, ri_len))
  
  # Shortcut it!
  # t_len = 10
  
  print('Generating blank UV_DATA rows...')
  tbl_uv_data = make_uv_data(num_rows=t_len*bl_len)

  
  print('Now filling FITS file with data from HDF file...')
  # The config function is in a seperate file, so import it
  import config_uv_data
  tbl_uv_data = config_uv_data.config_uv_data(h5,tbl_uv_data,shortcut=False)
  #print tbl_uv_data.header.ascardlist()
  print('\n')

  hdulist = pf.HDUList(
              [hdu, 
              tbl_array_geometry,
              tbl_frequency,
              tbl_antenna,
              tbl_source, 
              # tbl_flag,
              # tbl_bandpass,
              # tbl_gain_curve,
              # tbl_interferometer_model,
              tbl_system_temperature,
              # tbl_phase_cal,
              tbl_uv_data
              ])
  
  print('Verifying integrity...')            
  hdulist.verify()
  

  if(os.path.isfile(fitsfile)):
    print('Removing existing file...')
    os.remove(fitsfile)
  print('Writing to file...')
  hdulist.writeto(fitsfile)

  print('Done.')


if __name__ == '__main__':
  main()
  
