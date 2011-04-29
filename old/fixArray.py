# encoding: utf-8
"""
fixArray.py

Created by Danny Price on 2011-04-26.
Copyright (c) 2011 The University of Oxford. All rights reserved.
"""

import sys, os
import pyfits as pf, numpy as np,  tables as tb

def config_array_geometry(tbl):
  """
  Configures the array_geometry table with Medicina values
  """
  
  geometry = tbl.data

  # We are at Medicina, Italy
  (latitude, longitude, elevation) = ('44:31:24.88', '11:38:45.56', 28)
  
  # Antenna positions are relative to the array centre
  
  # X-Y-Z in nanoseconds
  xyz_ns = np.array([[ -11.69,  -85.50,   11.89],  #3
         [ -11.69,  -65.90,   11.89],  #2
         [ -11.69,  -46.29,   11.89],  #1
         [ -11.69,  -26.68,   11.89],  #0
         [ -35.08,  -85.50,   35.67],  #7
         [ -35.08,  -65.90,   35.67],  #6
         [ -35.08,  -46.29,   35.67],  #5
         [ -35.08,  -26.68,   35.67],  #4
         [ -58.47,  -85.50,   59.45],  #11
         [ -58.47,  -65.90,   59.45],  #10
         [ -58.47,  -46.29,   59.45],  #9
         [ -58.47,  -26.68,   59.45],  #8
         [ -81.86,  -85.50,   83.23],  #15
         [ -81.86,  -65.90,   83.23],  #14
         [ -81.86,  -46.29,   83.23],  #13
         [ -81.86,  -26.68,   83.23],  #12
         [-105.25,  -85.50,  107.01],  #19
         [-105.25,  -65.90,  107.01],  #18
         [-105.25,  -46.29,  107.01],  #17
         [-105.25,  -26.68,  107.01],  #16
         [-128.64,  -85.50,  130.80],  #23
         [-128.64,  -65.90,  130.80],  #22
         [-128.64,  -46.29,  130.80],  #21
         [-128.64,  -26.68,  130.80],  #20
         [-152.03,  -85.50,  154.58],  #27
         [-152.03,  -65.90,  154.58],  #26
         [-152.03,  -46.29,  154.58],  #25
         [-152.03,  -26.68,  154.58],  #24
         [-175.42,  -85.50,  178.36],  #31
         [-175.42,  -65.90,  178.36],  #30
         [-175.42,  -46.29,  178.36],  #29
         [-175.42,  -26.68,  178.36]],  #28
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
  
def main():
  hdffile  = 'cygnus.h5c'
  fitsfile = 'cygnus.fits'
  

  print('Opening HDF5 and FITS IDI tables')
  print('--------------------------------')  
  # Open hdf5 table
  print("opening HDF5 table...")
  print("opening fits template")
  fits = pf.open(fitsfile, mode='update')
  

  # Go through and generate required tables
  print('Fixing ARRAY_GEOMETRY')
  print('------------------------------------')  
  tbl_array_geometry = fits[1]
  tbl_array_geometry = config_array_geometry(tbl_array_geometry)
  fits[1] = tbl_array_geometry
  #print tbl_array_geometry.header.ascardlist()
  print(' writing back to file... \n')
  
  fits.flush()
  fits.close()

if __name__ == '__main__':
  main()
