# encoding: utf-8
"""
createMedicinaFITS.py
=====================

Creates a FITS IDI file for Medicina BEST-2 radio telescope.
An XML file is used to generate the table headers, and the table
data is either generated from functions within this file, or from
a HDF5 file (i.e. the raw output of a correlator).

Created by Danny Price on 2011-04-21.
Copyright (c) 2011 The University of Oxford. All rights reserved.

"""

import sys, os, datetime, time
import pyfits as pf, numpy as np,  tables as tb
import ephem

# FITS IDI python module imports
from pyFitsidi import *
from astroCoords import *

# Some global definitions that I don't think I really use
global earth_radius, light_speed, pi, freq
earth_radius = 6371 * 10**3     # Earth's radius
light_speed = 299792458         # Speed of light
pi = np.pi                      # Pi
freq = 408 *10**6               # 408 MHz


#########################
#   CLASSES & HELPERS   #
#########################

class Array(ephem.Observer):
    """ An antenna array class.
    
        Based on pyEphem's Observer class.
        Probably very similar to the one in AIPY.
        
        Parameters
        ----------
        lat: dd:mm:ss
          latitude of array centre, e.g. 44:31:24.88
        long: dd:mm:ss
          longitude of array centre, e.g. 11:38:45.56
        elev: float
          elevation in metres of array centrem e.g. 28.0
        date: datetime object
          date and time of observation, e.g. datetime.now()
        antennas: np.array([x,y,z])
          numpy array of antenna positions, in xyz coordinates in meters,
          relative to the array centre.
        
    """
    def __init__(self, lat, long, elev, date, antennas):
        super(Array, self).__init__()
        self.lat = lat
        self.long = long
        self.elev = elev
        self.date = date
        self.antennas = antennas
    def update(self, date):
        """Update antenna with a new datetime"""
        self.date = date


def makeSource(name,ra,dec,flux=0,epoch=2000):
    """ Create a pyEphem FixedBody
    
    Parameters
    ----------
    name: string
      Name of source, e.g. CasA
    ra: hh:mm:ss
      right ascension, e.g. 23:23:26
    dec: dd:mm:ss
      declination e.g. 58:48:22.21
    flux: float
      flux brightness in Jy (not actually used here)
    epoch: J2000
      Defaults to J2000, i.e. 2000"
    """
    line = "%s,f,%s,%s,%s,%d"%(name,ra,dec,flux,epoch)
    body = ephem.readdb(line)
    return body

def computeUVW(xyz,H,d):
  """ Converts X-Y-Z coordinates into U-V-W
  
  Uses the transform from Thompson Moran Swenson (4.1, pg86)
  
  Parameters
  ----------
  xyz: should be a numpy array [x,y,z]
  H: float (degrees)
    is the hour angle of the phase reference position
  d: float (degrees)
    is the declination
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


def ant_array():
  """ The antenna array for Medicina. 
  This doesn't really need to be a function.
  """
  
  # We are at Medicina, Italy
  # http://www.oc.nps.edu/oc2902w/coord/llhxyz.htm
  # ECEF from Latitude,Longitude, Height (ellipsoidal)
  # X : 4461.122   km
  # Y : 919.469   km
  # Z : 4449.776   km
  (latitude, longitude, elevation) = ('44:31:24.88', '11:38:45.56', 28) 
  
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
  
  return xyz_m
  

########################
#   CONFIG FUNCTIONS   #
########################

def config_antenna(tbl):
  """ Configures the antenna table.
  
  Parameters
  ----------
  tbl: pyfits.hdu
    table to be configured
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

def config_source(tbl, source):
  """  Configures the source table.
  
  Parameters
  ----------
  tbl: pyfits.hdu
    table to be configured
  source: ephem.fixedBody
    source to be phased to (use makeSource())
  """
  
  # Stupidly using source as a variable name twice
  source_ra   = np.rad2deg(source._ra)
  source_dec  = np.rad2deg(source._dec)
  source_name = source.name
  
  print('Source is: %s'%source.name)
  
  source = tbl.data[0]
  
  source['SOURCE_ID'] = 1
  source['SOURCE']    = source_name
  source['VELDEF']    = 'RADIO'
  source['VELTYP']    = 'GEOCENTR'
  source['FREQID']    = 1
  source['RAEPO']     = source_ra
  source['DECEPO']    = source_dec
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
  Configures the frequency table.
  
  Parameters
  ----------
  tbl: pyfits.hdu
    table to be configured
  """

  frequency = tbl.data[0]

  frequency['FREQID']         = 1
  frequency['BANDFREQ']       = 0         # This is offset from REF_FREQ, so zero!
  frequency['CH_WIDTH']       = 20.0/1024.0 * 10**6
  frequency['TOTAL_BANDWIDTH']= 20*10**6
  frequency['SIDEBAND']       = 1

  tbl.data[0] = frequency

  return tbl  

def config_array_geometry(tbl, antenna_array):
  """  Configures the array_geometry table with Medicina values

  Parameters
  ----------
  tbl: pyfits.hdu
    table to be configured
  antenna_array: numpy.array
    an array of xyz coordinates of the antenna locations (offsets) in METERS
    from the array centre (this is a keyword in the header unit)
    e.g. 
  """
  
  geometry = tbl.data

  # X-Y-Z in metres
  xyz_m = antenna_array

  for i in range(0,tbl.data.size):
    geometry[i]['ANNAME']  = 'MED_%i'%i
    geometry[i]['STABXYZ'] = xyz_m[i]
    geometry[i]['DERXYZ']  =  0
    #geometry[i]['ORBPARM'] = 0
    geometry[i]['NOSTA']   = i
    geometry[i]['MNTSTA']  = 1 
    # NOTE: Aperture arrays are given code 6, but not supported by CASA
    geometry[i]['STAXOF']  = np.array([0,0,0])
    geometry[i]['DIAMETER'] = 0

  tbl.data = geometry

  return tbl

def config_system_temperature(tbl):
  """
  Configures the system_temperature table with values for Medicina.
  Casa currently doesn't support this table in any way.
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


def config_uv_data(h5, tbl_uv_data, antenna_array, source):
  
  print('\nGenerating file metadata')
  print('--------------------------')

  # Data is stored in multidimensional array called xeng_raw0
  # time, channels, baselines, polarisation, then data=(real, imaginary) 
  (t_len, chan_len, bl_len, pol_len, ri_len) = h5.root.xeng_raw0.shape
  h5data = h5.root.xeng_raw0
    
  timestamps = []
  baselines = []
  weights = [1  in range(0,2048)]
  
  print('Retrieving timestamps...')
  for t in range(0,t_len):
    timestamp = h5.root.timestamp0[t]
    timestamps.append(timestamp)


  # Date and time
  # Date is julian date at midnight that day
  # The time is DAYS since midnight
  firststamp = timestamps[0]
  julian = ephem.julian_date(time.gmtime(firststamp)[:6])
  
  midnight = int(firststamp)
  
  # Ephem returns julian date at NOON, we need at MIDNIGHT
  julian_midnight = int(julian)+1

  elapsed = []
  for timestamp in timestamps:
    # time = ephem.julian_date(datetime.datetime.fromtimestamp(timestamp))
    # t = ephem.julian_date(time.gmtime(timestamps[0])[:6])
    elapsed.append((ephem.julian_date(time.gmtime(timestamp)[:6]) - julian_midnight))

    
  print('Creating baseline IDs...')
  bl_order = h5.root.bl_order
  antennas = antenna_array.antennas
  for bl in range(0,bl_len):
    # Baseline is in stupid 256*baseline1 + baseline2 format
    ant1, ant2 = bl_order[bl][0], bl_order[bl][1] 
    bl_id = 256*ant1 + ant2
    
    # Generate the XYZ vectors too
    # From CASA measurement set definition
    # uvw coordinates for the baseline from ANTENNE2 to ANTENNA1, 
    # i.e. the baseline is equal to the difference POSITION2 - POSITION1. 
    bl_vector = antennas[ant2] - antennas[ant1]
    baselines.append((bl_id,bl_vector))  
    
  print('Computing UVW coordinates...\n')
  # Extract the timestamps and use these to make source our phase centre
  uvws = []
  for timestamp in timestamps:
    t = datetime.datetime.utcfromtimestamp(timestamp)
    print t
    antenna_array.update(t)
    source.compute(antenna_array)
  
    for baseline in baselines:
      vector = baseline[1]
      H, d = (antenna_array.sidereal_time() - source.ra, source.dec)
      uvws.append(computeUVW(vector,H,d))

  # This array has shape t_len, num_ants, 3
  # and units of SECONDS
  uvws = np.array(uvws)
  uvws = uvws.reshape(uvws.size/bl_len/3,bl_len,3) / light_speed


  print('\nReformatting HDF5 format -> FITS IDI UV_DATA')
  print('--------------------------------------------')
   
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
  print('\nCreating multidimensional UV matrix...')
  for t in range(0,t_len):
    print('processing time sample set %i/%i'%(t+1,t_len))
    for bl in range(0,bl_len):
      
      # Create a 1D index for the uv_data table
      i = t*bl_len + bl
      
      # Swap real and imaginary
      flux[:,0,0] = h5data[t,:,bl,0,1]
      flux[:,0,1] = h5data[t,:,bl,0,0]
      
      tbl_uv_data.data[i]['FLUX']     = flux.ravel()
      tbl_uv_data.data[i]['WEIGHT']   = weights
      
      tbl_uv_data.data[i]['UU']       = uvws[t][bl][0]
      tbl_uv_data.data[i]['VV']       = uvws[t][bl][1]
      tbl_uv_data.data[i]['WW']       = uvws[t][bl][2]
      
      # baselines is a list: [ (id, vec), (id,vec) ... ]
      tbl_uv_data.data[i]['BASELINE'] = baselines[bl][0]
      
      # Date and time
      # Date is julian date at midnight that day
      # The time is seconds since midnight
      tbl_uv_data.data[i]['DATE']     = julian_midnight
      tbl_uv_data.data[i]['TIME']     = elapsed[t]

      tbl_uv_data.data[i]['SOURCE']   = 1
      tbl_uv_data.data[i]['FREQID']   = 1
      tbl_uv_data.data[i]['INTTIM']   = 3
    
  print('\nData reformatting complete')
  
  h5.close()
  
  return tbl_uv_data  
  print('DONE.')


#####################
##       MAIN      ##
#####################

def main():
  """
  Main function call. This is the conductor.
  """
  
  print('\nInput and output filenames')
  print('--------------------------------')
  # What are the filenames for our datasets?
  hdffile  = '../for_danny.h5'
  fitsfile = '../for_danny.fits'
  configxml = 'config/medicina.xml'
  print "In: %s \nOut: %s\nConfig: %s"%(hdffile, fitsfile, configxml)
  
  print('\nConfiguring Array geography')
  print('--------------------------')
  # We are at Medicina, Italy
  (latitude, longitude, elevation) = ('44:31:24.88', '11:38:45.56', 28)
  now = datetime.datetime.now()
  
  # Let's make ourselves an Array (pyEphem observer)
  print('Location: Medicina BEST-2, Italy')
  array_geometry = ant_array()
  medicina = Array(lat=latitude, long=longitude,elev=elevation,date=now, antennas=array_geometry)

  print('\nConfiguring phase source')
  print('--------------------------')
  # The source is our phase centre for UVW coordinates
  CygA = makeSource(
      name="CygA",
      ra='19:59:28',
      dec='40:44:02',
      flux='1'
  )
  source = CygA
  source.compute(medicina)
  print "Name: %s \nRA: %s \nDEC: %s"%(source.name,source.ra,source.dec)
  
  # Make a new blank FITS HDU
  print('\nCreating PRIMARY HDU')
  print('------------------------------------')
  hdu = make_primary(config=configxml)
  print hdu.header.ascardlist()
  
  # Go through and generate required tables
  print('\nCreating ARRAY_GEOMETRY')
  print('------------------------------------')
  tbl_array_geometry = make_array_geometry(config=configxml, num_rows=32)
  tbl_array_geometry = config_array_geometry(tbl_array_geometry,array_geometry)
  print tbl_array_geometry.header.ascardlist()
  
  print('\nCreating FREQUENCY')
  print('------------------------------------')
  tbl_frequency = make_frequency(config=configxml, num_rows=1)
  tbl_frequency = config_frequency(tbl_frequency)
  print tbl_frequency.header.ascardlist()
  print('\n')

  print('\nCreating SOURCE')
  print('------------------------------------')
  tbl_source = make_source(config=configxml, num_rows=1)
  tbl_source = config_source(tbl_source, source)
  print tbl_source.header.ascardlist()
  print('\n')

  print('\nCreating ANTENNA')
  print('------------------------------------')
  tbl_antenna = make_antenna(config=configxml, num_rows=32)
  tbl_antenna = config_antenna(tbl_antenna)
  print tbl_antenna.header.ascardlist()
  print('\n')

  print('\nCreating UV_DATA')
  print('------------------------------------')
  # Open hdf5 table
  print('Opening HDF5 table %s'%hdffile)
  h5 = tb.openFile(hdffile)
  
  # Data is stored in multidimensional array called xeng_raw0
  # time, channels, baselines, polarisation, then data=(real, imaginary) 
  (t_len, chan_len, bl_len, pol_len, ri_len) = h5.root.xeng_raw0.shape
  print('Data dimensions: %i dumps, %i chans, %i baselines, %i pols, %i data (real/imag)'\
  %(t_len, chan_len, bl_len, pol_len, ri_len))
  
  print('Generating blank UV_DATA rows...')
  tbl_uv_data = make_uv_data(config=configxml, num_rows=t_len*bl_len)

  print('Now filling FITS file with data from HDF file...')
  # The config function is in a seperate file, so import it
  tbl_uv_data = config_uv_data(h5,tbl_uv_data, medicina, source)
  print tbl_uv_data.header.ascardlist()
  print('\n')

  hdulist = pf.HDUList(
              [hdu, 
              tbl_array_geometry,
              tbl_frequency,
              tbl_antenna,
              tbl_source, 
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