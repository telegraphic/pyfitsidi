# encoding: utf-8
"""
pyFitsidi.py
=============

Created by Danny Price on 2011-04-28.
Copyright (c) 2011 The University of Oxford. All rights reserved.

This file is a collection of modules for creating blank FITS IDI files.
It consists mainly of pretty basic functions to create blank tables.

The FITS handling is all done by pyFits, and blank arrays are created
with numpy. So you'll need to have both of these installed on your machine.
In addition, the config xml file is read with lxml, so install that too.


FITS-IDI Table Overview
~~~~~~~~~~~~~~~~~~~~~~~~

Here is a quick rundown of the tables that this script can make.
Not all these tables are mandatory, so I've starred the ones which are the most
important to understand and to get into your dataset.

* **ANTENNA**           Antenna polarization information
* **ARRAY_GEOMETRY**    Time system information and antenna coordinates
* FLAG                  Flagged data
* **FREQUENCY**         Frequency setups
* GAIN_CURVE            Antenna gain curves
* INTERFEROMETER_MODEL  Correlator model
* PHASE-CAL             Phase cal measurements
* **SOURCE**            Sources observed
* SYSTEM_TEMPERATURE    System and antenna temperatures
* **UV_DATA**           Visibility data

These tables are new from the FITS IDI update, and are all optional:

* BANDPASS              Bandpass functions
* BASELINE              Baseline-specific gain factors
* CALIBRATION           Gains as a function of time
* WEATHER               Meteorological data

Module listing
~~~~~~~~~~~~~~

"""

import sys, os
import pyfits as pf, numpy as np
from lxml import etree

def parseConfig(tagname, config='config.xml'):
  """ Finds tagname, in elementTree x, parses and returns dictionary of values
  This is a helper function, and is not usually called directly
  """
  
  xmlData = etree.parse(config) 
  x = xmlData.getroot()
  T = True # FITS just uses T for True, python (and pyFITS) uses True
  
  # cunning list comprehension with an eval()
  vals = dict([ (child.tag, eval(child.text.strip())) for child in x.find(tagname).getchildren()])
  return vals

def make_primary(config='config.xml'):
  """  Creates the primary header data unit (HDU). 
  
  This function generates header keywords from the file headers/primary.tpl
  
  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  """
  
  # Make a new blank FITS HDU
  hdu = pf.PrimaryHDU()
  
  # Generate headers from config file
  primary = parseConfig('PRIMARY', config)
  common  = parseConfig('COMMON', config)

  for key in primary: hdu.header.update(key, primary[key])
  for key in common: hdu.header.update(key, common[key])
  
  hdu.verify() # Will raise a warning if there's an issue  
  
  return hdu

def make_array_geometry(config='config.xml', num_rows=1):
  """Creates a vanilla ARRAY_GEOMETRY table HDU. 
  
  One row is required for each antenna in the array (num_rows)

  Notes
  -----
  Table is built with the following columns:
  
  * ANNAME: Antenna name
  * STABXYZ: Antenna relative position vector ECI components, in meters
  * DERXYZ: Antenna velocity vector components, in meters/sec
  * ORBPARM: Orbital parameters
  * NOSTA: Antenna ID number for station
  * MNTSTA: Antenna mount type (0 is alt-azimuth)
  * STAXOF: Antenna axis offset, in meters
  * DIAMETER: Antenna diameter (optional)

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
  """
  
  # Generate the columns for the table header
  c = []

  c.append(pf.Column(name='ANNAME',  format='8A',\
    array=np.zeros(num_rows,dtype='a8')))   
  
  c.append(pf.Column(name='STABXYZ', format='3D', \
    unit='METERS',array=np.zeros(num_rows,dtype='3float64')))
  
  c.append(pf.Column(name='DERXYZ',  format='3E', \
    unit='METERS/SEC', array=np.zeros(num_rows,dtype='3float32')))
  
  c.append(pf.Column(name='ORBPARM', format='1D',\
    array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='NOSTA',   format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='MNTSTA',  format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='STAXOF',  format='3E', \
    unit='METERS', array=np.zeros(num_rows,dtype='3float32')))

  c.append(pf.Column(name='DIAMETER',  format='1E', \
    unit='METERS', array=np.zeros(num_rows,dtype='float32')))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  # Generate headers from config file
  array_geometry = parseConfig('ARRAY_GEOMETRY', config)
  common  = parseConfig('COMMON', config)

  for key in array_geometry: tblhdu.header.update(key, array_geometry[key])
  for key in common: tblhdu.header.update(key, common[key])
  
  return tblhdu
    
def make_antenna(config='config.xml', num_rows=1):
  """  Creates a vanilla ANTENNA table HDU
  
  Notes
  -----
  CASA didn't like importing POLCALA and POLCALB, so they are currently commented out.
  
  Table is built with the following columns:
  
  * TIME: Difference of antenna table time interval centre time and RDATE 0 hours
  * TIME_INTERVAL: Antenna table time interval width
  * ANNAME: Antenna name, should match value in ARRAY_GEOMETRY
  * ANTENNA_NO: Antemma ID number for station
  * ARRAY:    Array ID number
  * FREQID:   Frequency setup ID number
  * NO_LEVELS:Number of digitiser levels
  * POLYTYA:  Feed A polarisation direction
  * POLAA:    Feed A polarisation (degrees)
  * POLCALA:  Feed A polarisation parameters
  * POLYTYB:  As above, for feed B
  * POLAB:    As above, for feed B
  * POLCALB:  As above, for feed B

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
  """

  c = []
  
  c.append(pf.Column(name='TIME', format='1D',\
   unit='DAYS',array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='TIME_INTERVAL', format='1E',\
    unit='DAYS', array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='ANNAME', format='8A',\
    array=np.zeros(num_rows,dtype='a8')))
  
  c.append(pf.Column(name='ANTENNA_NO', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='ARRAY', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='FREQID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='NO_LEVELS',  format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='POLTYA', format='1A',\
    array=np.zeros(num_rows,dtype='a1')))
  
  c.append(pf.Column(name='POLAA', format='1E',\
    unit='DEGREES', array=np.zeros(num_rows,dtype='float32')))
  
  # nb: Was encontering errors with CASA with this column
  #c.append(pf.Column(name='POLCALA', format='1E',\
  #  array=np.zeros(32,dtype='float32')))
  
  c.append(pf.Column(name='POLTYB', format='1A',\
    array=np.zeros(num_rows,dtype='a1')))
  
  c.append(pf.Column(name='POLAB', format='1E',\
    unit='DEGREES', array=np.zeros(num_rows,dtype='float32')))

  # nb: Was encontering errors with CASA with this column  
  #c.append(pf.Column(name='POLCALB', format='1E',\
  #  array=np.zeros(32,dtype='float32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  # Generate headers from config file
  cards = parseConfig('ANTENNA', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])

  return tblhdu

def make_frequency(config='config.xml', num_rows=1):
  """ Creates a vanilla FREQUENCY table HDU
  
  Notes
  -----
  Table is built with the following columns:
  
  * FREQID:   Frequency setup ID number
  * BANDFREQ: Frequency band base offset (Hz)
  * CH_WIDTH: Frequency channel width (Hz)
  * TOTAL_BANDWIDTH: Frequency bandwidth (Hz)
  * SIDEBAND: Sideband flag (1 indicates upper sideband)
  * BB_CHAN:  ? 

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
  """

  c = []
  
  c.append(pf.Column(name='FREQID',   format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='BANDFREQ', format='1D',\
    unit='HZ', array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='CH_WIDTH', format='1E',\
    unit='HZ', array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='TOTAL_BANDWIDTH', format='1E',\
    unit='HZ', array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='SIDEBAND', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  # Not really sure what this does, so commented it out
  #c.append(pf.Column(name='BB_CHAN',  format='1J',\
  #  array=np.zeros(num_rows,dtype='int32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  # Generate headers from config file
  cards = parseConfig('FREQUENCY', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])
  
  return tblhdu
  
def make_bandpass(config='config.xml', num_rows=1):
  """ Creates a vanilla BANDPASS table HDU
  
  Notes
  -----
  Table is built with the following columns:

  * TIME: Difference of bandpass table time int center time and RDATE 0 hours
  * TIME_INTERVAL: Bandpass table time interval width
  * SOURCE_ID:  Source ID number
  * ANTENNA_NO: Antenna ID number for station
  * ARRAY:      Array ID number
  * FREQID:     Frequency setup ID number (should match ANTENNA)
  * BANDWIDTH:  Frequency band width described by bandpass
  * BAND_FREQ:  Frequency band base offset
  * REFANT_1:   Reference antenna ID number
  * BREAL_1:    Bandpass response real componet
  * BIMAG_1:    Bandpass response imaginary component

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
  """
  c = []
  
  c.append(pf.Column(name='TIME', format='1D',\
   unit='DAYS', array=np.zeros(num_rows,dtype='float64')))
   
  c.append(pf.Column(name='TIME_INTERVAL', format='1E',\
   unit='DAYS',array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='SOURCE_ID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='ANTENNA_NO',format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='ARRAY',     format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='FREQID',    format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='BANDWIDTH', format='1E',\
    unit='HZ', array=np.zeros(num_rows,dtype='float32')))
    
  c.append(pf.Column(name='BAND_FREQ', format='1D',\
   unit='HZ', array=np.zeros(num_rows,dtype='float64')))
   
  c.append(pf.Column(name='REFANT_1',  format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='BREAL_1',  format='1024E',\
    array=np.zeros(num_rows,dtype='1024float32')))
    
  c.append(pf.Column(name='BIMAG_1',  format='1024E',\
    array=np.zeros(num_rows,dtype='1024float32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  # Generate headers from config file
  cards = parseConfig('BANDPASS', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])
    
  return tblhdu  

def make_source(config='config.xml', num_rows=1):
  """ Creates a vanilla SOURCE table HDU

  Notes
  -----
  Table is built with the following columns:
  
  * SOURCE_ID Source ID number
  * SOURCE    Source name
  * QUAL      Source qualifier number.
  * CALCODE   Source calibrator code. 
  * FREQID    Source frequency ID
  * IFLUX     Source I flux density
  * QFLUX     Source Q flux density
  * UFLUX     Source U flux density
  * VFLUX     SourceV flux density
  * ALPHA     Source spectral index
  * FREQOFF   Source frequency offset
  * RAEPO     Source J2000 equatorial position RA coordinate
  * DECPO     Source J2000 equatorial position DEC coordinate
  * EQUINOX   Mean Equinox
  * RAAPP     Source apparent equatorial position RA coordinate
  * DECAPP    Source apparent equatorial position DEC coordinate
  * SYSVEL    Systematic velocity.
  * VELTYP    Systematic velocity reference frame.
  * VELDEF    Systematic velocity convention.
  * RESTFREQ  Line rest frequency.
  * PMRA      Source proper motion RA coordinate
  * PMDEC     Source proper motion DEC coordinate
  * PARALLAX  Source parallax. 

Parameters
----------
config: string
  filename of xml configuration file, defaults to 'config,xml'
num_rows: int
  number of rows to generate. Rows will be filled with numpy zeros.
  """

  c=[]

  c.append(pf.Column(name='SOURCE_ID',    format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='SOURCE',   format='16A',\
    array=np.zeros(num_rows,dtype='16a')))
    
  c.append(pf.Column(name='QUAL',     format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='CALCODE',  format='4A',\
    array=np.zeros(num_rows,dtype='4a')))
    
  c.append(pf.Column(name='FREQID',   format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='IFLUX',    format='1E',\
    array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='QFLUX',    format='1E',\
    array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='UFLUX',    format='1E',\
    array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='VFLUX',    format='1E',\
    array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='ALPHA',    format='1E',\
    array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='FREQOFF',  format='1E',
    array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='RAEPO',    format='1D',\
   unit='DEGREES', array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='DECEPO',    format='1D',\
   unit='DEGREES', array=np.zeros(num_rows, dtype='float64')))
  
  c.append(pf.Column(name='EQUINOX',    format='8A',\
    array=np.zeros(num_rows,dtype='8a')))
    
  c.append(pf.Column(name='RAAPP',    format='1D',\
   unit='DEGREES', array=np.zeros(num_rows,dtype='float64')))
   
  c.append(pf.Column(name='DECAPP',   format='1D',\
   unit='DEGREES', array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='SYSVEL',   format='1D',\
    unit='METERS/SEC', array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='VELTYP',   format='8A',\
    array=np.zeros(num_rows,dtype='8a')))
  
  c.append(pf.Column(name='VELDEF',   format='8A',\
    array=np.zeros(num_rows,dtype='8a')))
  
  c.append(pf.Column(name='RESTFREQ', format='1D',\
   unit='HZ', array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='PMRA',     format='1D',\
   unit='DEGREES/DAY', array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='PMDEC',    format='1D',\
   unit='DEGREES/DAY', array=np.zeros(num_rows,dtype='float64')))
  
  c.append(pf.Column(name='PARALLAX', format='1E',\
   unit='ARCSEC', array=np.zeros(num_rows,dtype='float32')))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  # Generate headers from config file
  cards = parseConfig('SOURCE', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])
      
  return tblhdu

def make_uv_data(config='config.xml', num_rows=1):
  """ Creates a vanilla UV_DATA table HDU
  
  Parameters
  ----------
  num_rows
    Number of rows in your UV dataset. For example, if you have 528 baselines 
    (inc. autocorr), then for 10 time dumps, you'll need 10*528 rows
  
  Notes
  -----
  Table is built with the following columns:
  
  * UU           Baseline vector U coordinate (seconds)
  * VV           Baseline vector V coordinate
  * WW           Baseline vector W coordinate
  * DATE         UTC Julian day value for time 00:00:00  on the day of the observation
  * TIME         Fraction of Julian day from midnight to timestamp on day of observation.
  * BASELINE     Antenna baseline pair ID.
  * FILTER       VLBA filter ID
  * SOURCE       Data source ID
  * FREQID       Data frequency setup ID
  * INTTIM       Data integration time
  * WEIGHT       Data weights (one element for each freq channel)
  * GATEID       VLBA gate ID
  * FLUX         UV visibility data matrix
  
  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
    
  """
  c = []                
  
  
                                          
  c.append(pf.Column(name='UU', format='1E',\
    unit='SECONDS', array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='VV',  format='1E',\
    unit='SECONDS', array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='WW',        format='1E',\
    unit='SECONDS', array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='DATE',      format='1D',\
    unit='DAYS', array=np.zeros(num_rows,dtype='float64')))
   
  c.append(pf.Column(name='TIME',      format='1D',\
    unit='DAYS', array=np.zeros(num_rows,dtype='float64')))
   
  c.append(pf.Column(name='BASELINE',  format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='SOURCE',    format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='FREQID',    format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='INTTIM',    format='1E',\
    unit='SECONDS', array=np.zeros(num_rows,dtype='float32')))
    
  c.append(pf.Column(name='WEIGHT',    format='2048E',\
    array=np.zeros(num_rows,dtype='2048float32')))
    
  c.append(pf.Column(name='FLUX',      format='2048E',\
    unit='UNCALIB', array=np.zeros(num_rows,dtype='2048float32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  # Generate headers from config file
  cards = parseConfig('UV_DATA', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key]) 
        
  return tblhdu

def make_interferometer_model(config='config.xml', num_rows=1):
  """
  Creates a vanilla INTERFEROMETER_MODEL table HDU.

  Notes
  -----
  This table is optional, and is not included in Medicina FITS IDI
  
  Table is built with the following columns:

   
  * TIME          Starting time of interval
  * TIME_INTERVAL Duration of interval
  * SOURCE_ID     Source ID number
  * ANTENNA_NO    Antenna number
  * ARRAY         Array number
  * FREQID        Frequency setup number
  * I.FAR.ROT     Ionospheric Faraday rotation
  * FREQ_VAR      Time-variable frequency offsets
  * PDELAY_1      Phase delay polynomials for polarization 1
  * GDELAY_1      Group delay polynomials for polarization 1
  * PRATE_1       Phase delay rate polynomials for polarization 1
  * GRATE_1       Group rate polynomials for polarization 1
  * DISP_1        Dispersive delay for polarization 1 at 1m wavelength
  * DDISP_1       Rate of change of dispersive del for pol 1 at 1m

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
    
  """
  
  c = []
                                        
  c.append(pf.Column(name='TIME', format='1D',\
   unit='DAYS', array=np.zeros(num_rows,dtype='float64')))
   
  c.append(pf.Column(name='TIME_INTERVAL',format='1E',\
   unit='DAYS', array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='SOURCE_ID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='ANTENNA_NO', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='ARRAY', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='FREQID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='I.FAR.ROT',    format='1E',\
    unit='RAD/M**2', array=np.zeros(num_rows,dtype='float32')))
    
  c.append(pf.Column(name='FREQ.VAR',     format='1E',\
    unit='HZ', array=np.zeros(num_rows,dtype='float32')))
    
  c.append(pf.Column(name='PDELAY_1',     format='1E',\
   unit='TURNS', array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='GDELAY_1',     format='1E',\
   unit='SECONDS',array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='PRATE_1', format='1E',\
   unit='HZ', array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='GRATE_1', format='1E',\
   unit='SEC/SEC', array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='DISP_1', format='1E',\
   unit='SECONDS', array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='DDISP_1', format='1E',\
   unit='SEC/SEC', array=np.zeros(num_rows,dtype='float32')))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  # Generate headers from config file
  cards = parseConfig('INTERFEROMETER_MODEL', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])
       
  return tblhdu      
                                    
def make_system_temperature(config='config.xml', num_rows=1):
  """ Creates a vanilla SYSTEM_TEMPERATURE table HDU
  
  Notes
  -----
  This is an optional table.
  Todo: add dual pol support.
  
  Table is built with the following columns:
  
  * TIME          Central time of interval covered
  * TIME_INTERVAL Duration of interval
  * SOURCE_ID     Source ID number
  * ANTENNA_NO    Antenna number
  * ARRAY         Array number
  * FREQID        Frequency setup number
  * TSYS_1        System temperatures for polarization 1
  * TANT_1        Antenna temperatures for polarization 1

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
  """
  c = []
  
  c.append(pf.Column(name='TIME',  format='1D',\
   unit='DAYS', array=np.zeros(num_rows,dtype='float64')))
   
  c.append(pf.Column(name='TIME_INTERVAL',  format='1E',\
   unit='DAYS', array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='SOURCE_ID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='ANTENNA_NO', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='ARRAY', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='FREQID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='TSYS_1', format='1E',\
   unit='KELVIN', array=np.zeros(num_rows,dtype='float32')))
   
  c.append(pf.Column(name='TANT_1', format='1E',\
   unit='KELVIN', array=np.zeros(num_rows,dtype='int32')))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  # Generate headers from config file
  cards = parseConfig('SYSTEM_TEMPERATURE', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])
  
  return tblhdu   

def make_gain_curve(config='config.xml', num_rows=1):
  """ Creates a vanilla GAIN_CURVE table HDU
    
  Notes
  --------------------------------
  This is an optional table (we will not include it). 
  Todo: Add switch to allow dual polarisation.
  
  Table is built with the following columns:
  
  * ANTENNA_NO  Antenna number
  * ARRAY       Array number
  * FREQID      Frequency setup number
  * TYPE_1      Gain curve types for polarization 1
  * NTERM_1     Numbers of terms or entries for polarization 1
  * X_TYP_1     x value types for polarization 1
  * Y_TYP_1     y value types for polarization 1
  * X_VAL_1     x values for polarization 1
  * Y_VAL_1     y values for polarization 1
  * GAIN_1      Relative gain values for polarization 1
  * SENS_1      Sensitivities for polarization 1

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
    
  """

  c = []
  
  c.append(pf.Column(name='ANTENNA_NO', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='ARRAY', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
    
  c.append(pf.Column(name='FREQID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='TYPE_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='NTERM_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='X_TYP_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='Y_TYP_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='X_VAL_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='Y_VAL_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='GAIN_1', format='1E',\
    array=np.zeros(num_rows,dtype='float32')))
  
  c.append(pf.Column(name='SENS_1', format='1E',\
   unit='K/JY', array=np.zeros(num_rows,dtype='float32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  # Generate headers from config file
  cards = parseConfig('GAIN_CURVE', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])

  return tblhdu

def make_phase_cal(config='config.xml', num_rows=1):
  """ Creates a vanilla PHASE-CAL table HDU


  Notes
  -------
  This is an optional table (we will not include it)
  
  Table is built with the following columns:
  
  * TIME          Central time of interval covered
  * TIME_INTERVAL Duration of interval
  * SOURCE_ID     Source ID number
  * ANTENNA_NO    Antenna number
  * ARRAY         Array number
  * FREQID        Frequency setup number
  * CABLE_CAL     Cable calibration measurement
  * STATE_1       State counts for polarization 1
  * PC_FREQ_1     Phase cal tone frequencies for polarization 1
  * PC_REAL_1     real parts of phase-cal measurements for pol 1
  * PC_IMAG_1     imaginary parts of phasecal measurements for pol 1
  * PC_RATE_1     phase-cal rates for polarization 1

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
    
  """

  c = []
                                        
  c.append(pf.Column(name='TIME', format='1D',\
    array=np.zeros(num_rows,dtype='float64'), unit='DAYS'))
    
  c.append(pf.Column(name='TIME_INTERVAL', format='1E',\
   unit='DAYS', array=np.zeros(num_rows,dtype='float32')))

  c.append(pf.Column(name='SOURCE_ID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='ANTENNA_NO', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='ARRAY', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='FREQID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='CABLE_CAL', format='1E',\
   unit='SECONDS', array=np.zeros(num_rows,dtype='float32')))

  c.append(pf.Column(name='STATE_1', format='1J',\
   unit='PERCENT', array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='PC_FREQ_1', format='1J',\
   unit='HZ', array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='PC_REAL_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='PC_IMAG_1', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  c.append(pf.Column(name='PC_RATE_1', format='1J',\
   unit='SEC/SEC', array=np.zeros(num_rows,dtype='int32')))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  # Generate headers from config file
  cards = parseConfig('PHASE_CAL', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])
    
  return tblhdu

def make_flag(config='config.xml', num_rows=1):
  """ Creates a vanilla FLAG table HDU
  

  Notes
  ----------
  This table is optional.
  
  Table is built with the following columns:

  * SOURCE_ID Source ID number
  * ARRAY     Array number
  * ANTS      Antenna numbers
  * FREQID    Frequency setup number
  * TIMERANG  Time range
  * BANDS     Band flags
  * CHANS     Channel range
  * PFLAGS    Polarization flags
  * REASON    Reason for flag
  * SEVERITY  Severity code

  Parameters
  ----------
  config: string
    filename of xml configuration file, defaults to 'config,xml'
  num_rows: int
    number of rows to generate. Rows will be filled with numpy zeros.
  """

  c = []
    
  c.append(pf.Column(name='SOURCE_ID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='ARRAY', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='ANTS', format='2J',\
    array=np.zeros(num_rows,dtype='2int32')))
  
  c.append(pf.Column(name='FREQID', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='TIMERANG', format='2E',\
    unit='DAYS', array=np.zeros(num_rows,dtype='2float32')))
  
  c.append(pf.Column(name='BANDS', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))
  
  c.append(pf.Column(name='CHANS', format='2J',\
    array=np.zeros(num_rows,dtype='2int32')))
  
  c.append(pf.Column(name='PFLAGS', format='4J',\
    array=np.zeros(num_rows,dtype='4int32')))
  
  c.append(pf.Column(name='REASON', format='24A',\
    array=np.zeros(num_rows,dtype='a24')))
  
  c.append(pf.Column(name='SEVERITY', format='1J',\
    array=np.zeros(num_rows,dtype='int32')))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  # Generate headers from config file
  cards = parseConfig('FLAG', config)
  common  = parseConfig('COMMON', config)

  for key in cards: tblhdu.header.update(key, cards[key])
  for key in common: tblhdu.header.update(key, common[key])
    
  return tblhdu