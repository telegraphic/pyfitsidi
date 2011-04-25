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

import sys, os, datetime, time
import pyfits as pf, numpy as np, tables as tb
import ephem

global earth_radius, light_speed, pi, freq
earth_radius = 6371 * 10**3     # Earth's radius
light_speed = 299792458         # Speed of light
pi = np.pi                      # Pi
freq = 408 *10**6               # 408 MHz

class Array(ephem.Observer):
    """ An antenna array object,
        Based on pyEphem's Observer class
    """
    def __init__(self, lat, long, elev,date):
        super(Array, self).__init__()
        self.lat = lat
        self.long = long
        self.elev = elev
        self.date = date
    
    def update(self, date):
        """Update antenna with a new datetime"""
        self.date = date

def xyztouvw(xyz,H,d):
  """
  Converts X-Y-Z coordinates into U-V-W
  using the transform from Thompson Moran Swenson (4.1, pg86)
  
  xyz should be a numpy array [x,y,z]
  H is the hour angle of the phase reference position
  d is the declination
  """
  sin = np.sin
  cos = np.cos
  
  xyz = np.matrix(xyz) # Cast into a matrix
  
  trans= np.matrix([
    [sin(H),         cos(H),        0],
    [-sin(d)*cos(H), sin(d)*sin(H), cos(d)],
    [cos(d)*cos(H), -cos(d)*sin(H), sin(H)]
  ])
  
  uvw = trans * xyz.T
  
  uvw = np.array(uvw)
  
  return uvw[:,0]

def computeUVW(H, d):
  """
  Computes the UVW coordinates for a medicina observation
  H is the hour angle of the phase reference position
  d is the declination
  """
  
  # We are at Medicina, Italy
  # http://www.oc.nps.edu/oc2902w/coord/llhxyz.htm
  # ECEF from Latitude,Longitude, Height (ellipsoidal)
  # X : 4461.122   km
  # Y : 919.469   km
  # Z : 4449.776   km
  (latitude, longitude, elevation) = ('44:31:24.88', '11:38:45.56', 28) 
  
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
  
  uvw_list = []
  for xyz in xyz_m:
    uvw_list.append(xyztouvw(xyz, H, d))
  
  return uvw_list

def makeSource(name,ra,dec,flux=0,epoch=2000):
    """ Create a pyEphem FixedBody
        name: Name of source, e.g. CasA
        ra: right ascension, e.g. 23:23:26
        dec: declination e.g. 58:48
        flux: flux brightnessin Jyat 1GHz, e.g. 2720
        epoch: Defaults to J2000, i.e. 2000"
    """
    line = "%s,f,%s,%s,%s,%d"%(name,ra,dec,flux,epoch)
    body = ephem.readdb(line)
    return body

def main():
  hdffile  = 'cygnus.h5c'
  fitsfile = 'cygnus.fits'
  

  print('Opening HDF5 and FITS IDI tables')
  print('--------------------------------')  
  # Open hdf5 table
  print("opening HDF5 table...")
  h5 = tb.openFile(hdffile)
  print("opening fits template")
  fits = pf.open(fitsfile)
  tbl_uv_data = fits[5]
  

  print('\nReformatting HDF5 format -> FITS IDI UV_DATA')
  print('--------------------------------------------')
  # Data is stored in multidimensional array called xeng_raw0
  # time, channels, baselines, polarisation, then data=(real, imaginary) 
  (t_len, chan_len, bl_len, pol_len, ri_len) = h5.root.xeng_raw0.shape
  h5data = h5.root.xeng_raw0
  
  fluxes = []
  timestamps = []
  baselines = []
  weights = [1  in range(0,2048)]
  
  print('Retrieving timestamps...')
  for t in range(0,t_len):
    timestamp = h5.root.timestamp0[t]
    timestamps.append(timestamp)
  
  # The fits file needs julian date timestamps
  julian_timestamps = []
  for timestamp in timestamps:
    # time = ephem.julian_date(datetime.datetime.fromtimestamp(timestamp))
    t = ephem.julian_date(time.gmtime(timestamps[0])[:6])
    julian_timestamps.append(t)

    
  print('Creating baseline IDs...')
  for bl in range(0,bl_len):
    # Baseline is in stupid 256*baseline1 + baseline2 format
    baseline = 256*h5.root.bl_order[bl][0] + h5.root.bl_order[bl][1]
    baselines.append(baseline)
    
  print('Computing UVW coordinates...')
  # We are at Medicina, Italy
  (latitude, longitude, elevation) = ('44:31:24.88', '11:38:45.56', 28)
  # Let's make ourselves an Array (pyEphem observer)
  now = datetime.datetime.now()
  medicina = Array(lat=latitude, long=longitude,elev=elevation,date=now)
  
  # If we were pointing at zenith, we would therefore be
  H, d =(0, 44.523577777777774)
  
  # Now it's time for a real source
  CasA = makeSource(
      name="CasA",
      ra='23:23:26',
      dec='58:48',
      flux='2720'
  )
  
  uvws = []
  # Extract the timestamps and use these to make cygnus our phase centre
  for timestamp in timestamps:
    t = datetime.datetime.fromtimestamp(timestamp)
    medicina.update(t)
    CasA.compute(medicina)
  
    H, d = (CasA.alt * 180 / np.pi, CasA.az* 180 / np.pi)
    #print(H,d)
    uvws.append(computeUVW(H,d))
  
  # This array has shape t_len, num_ants, 3  
  uvws = np.array(uvws)
  
  exit()
  
  # The actual data matrix is stored per row as a multidimensional matrix
  # with the following mandatory axes:
  # COMPLEX     Real, imaginary, (weight)
  # STOKES      Stokes parameter
  # FREQ        Frequency (spectral channel)
  # RA          Right ascension of the phase center
  # DEC         Declination of the phase center 
  flux = np.ndarray(shape=(chan_len,1,ri_len))
   
  # This step takes ages.
  # I imagine there is some way to massage the hdf5 array
  # to do this a lot quicker than iterating over the indexes 
  print('Creating multidimensional UV matrix...')
  for t in range(0,t_len):
    print('processing time sample set %i/%i'%(t+1,t_len))
    for bl in range(0,bl_len):
      
      # Create an index for the 1D array
      i = t_len*t + bl
      
      # Swap real and imaginary
      flux[:,0,0] = h5data[t,:,bl,0,1]
      flux[:,0,1] = h5data[t,:,bl,0,0]
      
      tbl_uv_data.data[i]['FLUX'] = flux.ravel()
      tbl_uv_data.data[i]['WEIGHT']   = weights
      
      tbl_uv_data.data[i]['UU']       = uvws[t][0]
      tbl_uv_data.data[i]['VV']       = uvws[t][1]
      tbl_uv_data.data[i]['WW']       = uvws[t][2]
      tbl_uv_data.data[i]['BASELINE'] = baselines[bl]
      
      # Date and time
      # Date is julian date at midnight that day
      # The time is seconds since midnight
      julian_midnight = int(julian_timestamps[0])
      tbl_uv_data.data[i]['DATE']     = julian_midnight
      tbl_uv_data.data[i]['TIME']     = julian_timestamps[t] - julian_midnight

      tbl_uv_data.data[i]['SOURCE']   = 1
      tbl_uv_data.data[i]['FREQID']   = 1
      tbl_uv_data.data[i]['INTTIM']   = 3
    
  print('Data has been reformatted.')
  
  
  
  print('Filling array with data...')
  fits[5].data = tbl_uv_data.data
  print('Verifying data integrity...')
  fits.verify()
  
  print('\nWriting to file')
  print('---------------')  
  print "Finally, writing to a new file:"
  filename = 'cygnus.fits'
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

