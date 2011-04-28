# encoding: utf-8
"""
createFits.py
=============

Creates a fits file out of a template. Made for Medicina X engine FitsIDI
Based off the LWA Fits IDI, because it's well documented! Many of the
notes in this file are copied over from this document.

Created by Danny Price on 2011-04-20.
Copyright (c) 2011 The University of Oxford. All rights reserved.


FITS-IDI Binary Tables
----------------------
ANTENNA Antenna polarization information
ARRAY_GEOMETRY Time system information and antenna coordinates
FLAG Flagged data
FREQUENCY Frequency setups
GAIN_CURVE Antenna gain curves
INTERFEROMETER_MODEL Correlator model
PHASE-CAL Phase cal measurements
SOURCE Sources observed
SYSTEM_TEMPERATURE System and antenna temperatures
UV_DATA Visibility data

we are also using the BANDPASS table of the proposed others:
BANDPASS Bandpass functions
BASELINE Baseline-specific gain factors
CALIBRATION Gains as a function of time
WEATHER Meteorological data

"""

import sys, os
import pyfits as pf, numpy as np,  tables as tb

def generateCards(filename):
  """
  Parses a text file and generates a pyfits card list.
  Do NOT feed this a full FITS file, feed it only a human-readable 
  FITS header template. 
  
  A text file is opened, acard is created from each line, then verified. 
  If the line does not pass verification, no card is appended.
  """
  infile = open(filename)

  cards = pf.CardList()

  # Loop through each line, converting to a pyfits card
  for line in infile.readlines():
      line = line.rstrip('\n')
      if(line == 'END'):
        break
      else:
        c = pf.Card().fromstring(line)
        c.verify() # This will attempt to fix issuesx[1]
        cards.append(c)
        
  return cards

def make_array_geometry():
  """Creates a vanilla ARRAY_GEOMETRY table HDU.
  Table is built with the following columns:

  ARRAY_GEOMETRY table data
  -------------------------
  ANNAME:  Antenna name
  STABXYZ: Antenna relative position vector ECI components, in meters
  DERXYZ:  Antenna velocity vector components, in meters/sec
  ORBPARM: Orbital parameters
  NOSTA:   Antenna ID number for station
  MNTSTA:  Antenna mount type (0 is alt-azimuth)
  STAXOF:  Antenna axis offset, in meters
  
  optional:
  DIAMETER: Antenna diameter
  
  """
  
  # Generate the columns for the table header
  c = []

  c.append(pf.Column(name='ANNAME',  format='8A',\
    array=np.zeros(32,dtype='a8')))   
  
  c.append(pf.Column(name='STABXYZ', format='3D', \
    unit='METERS',array=np.zeros(32,dtype='3float64')))
  
  c.append(pf.Column(name='DERXYZ',  format='3E', \
    unit='METERS/SEC', array=np.zeros(32,dtype='3float32')))
  
  c.append(pf.Column(name='ORBPARM', format='1D',\
    array=np.zeros(32,dtype='float64')))
  
  c.append(pf.Column(name='NOSTA',   format='1J',\
    array=np.zeros(32,dtype='int32')))
  
  c.append(pf.Column(name='MNTSTA',  format='1J',\
    array=np.zeros(32,dtype='int32')))
  
  c.append(pf.Column(name='STAXOF',  format='3E', \
    unit='METERS', array=np.zeros(32,dtype='3float32')))

  c.append(pf.Column(name='DIAMETER',  format='1E', \
    unit='METERS', array=np.zeros(32,dtype='float32')))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  # Update the header with values from the header files
  cards = generateCards('headers/array_geometry.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)
  
  return tblhdu
    
def make_antenna():
  """
  Creates a vanilla ANTENNA table HDU
  Table is built with the following columns:
  
  ANTENNA table data
  -------------------
  TIME:   Difference of antenna table time interval centre time and
          RDATE 0 hours
  TIME_INTERVAL: Antenna table time interval width
  ANNAME: Antenna name, should match value in ARRAY_GEOMETRY
  ANTENNA_NO: Antemma ID number for station
  ARRAY:    Array ID number
  FREQID:   Frequency setup ID number
  NO_LEVELS:Number of digitiser levels
  POLYTYA:  Feed A polarisation direction
  POLAA:    Feed A polarisation (degrees)
  POLCALA:  Feed A polarisation parameters
  POLYTYB:  As above, for feed B
  POLAB:    As above, for feed B
  POLCALB:  As above, for feed B
  """
  
  c = []
  
  c.append(pf.Column(name='TIME', format='1D',\
   unit='DAYS',array=np.zeros(32,dtype='float32')))
   
  c.append(pf.Column(name='TIME_INTERVAL', format='1E',\
    unit='DAYS', array=np.zeros(32,dtype='float32')))
  
  c.append(pf.Column(name='ANNAME', format='8A',\
    array=np.zeros(32,dtype='a8')))
  
  c.append(pf.Column(name='ANTENNA_NO', format='1J',\
    array=np.zeros(32,dtype='int32')))
  
  c.append(pf.Column(name='ARRAY', format='1J',\
    array=np.zeros(32,dtype='int32')))
  
  c.append(pf.Column(name='FREQID', format='1J',\
    array=np.zeros(32,dtype='int32')))
  
  c.append(pf.Column(name='NO_LEVELS',  format='1J',\
    array=np.zeros(32,dtype='int32')))
  
  c.append(pf.Column(name='POLTYA', format='1A',\
    array=np.zeros(32,dtype='a1')))
  
  c.append(pf.Column(name='POLAA', format='1E',\
    unit='DEGREES', array=np.zeros(32,dtype='float32')))
  
  #c.append(pf.Column(name='POLCALA', format='1E',\
  #  array=np.zeros(32,dtype='float32')))
  
  c.append(pf.Column(name='POLTYB', format='1A',\
    array=np.zeros(32,dtype='a1')))
  
  c.append(pf.Column(name='POLAB', format='1E',\
    unit='DEGREES', array=np.zeros(32,dtype='float32')))
  
  #c.append(pf.Column(name='POLCALB', format='1E',\
  #  array=np.zeros(32,dtype='float32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  cards = generateCards('headers/antenna.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  return tblhdu

def make_frequency():
  """
  Creates a vanilla FREQUENCY table HDU
  Table is built with the following columns:
  
  FREQUENCY table data
  --------------------
  FREQID:   Frequency setup ID number
  BANDFREQ: Frequency band base offset (Hz)
  CH_WIDTH: Frequency channel width (Hz)
  TOTAL_BANDWIDTH: Frequency bandwidth (Hz)
  SIDEBAND: Sideband flag (1 indicates upper sideband)
  BB_CHAN:  ? 
  
  """
  
  c = []
  
  c.append(pf.Column(name='FREQID',   format='1J',\
    array=np.zeros(1,dtype='int32')))
    
  c.append(pf.Column(name='BANDFREQ', format='1D',\
    unit='HZ', array=np.zeros(1,dtype='float64')))
  
  c.append(pf.Column(name='CH_WIDTH', format='1E',\
    unit='HZ', array=np.zeros(1,dtype='float32')))
  
  c.append(pf.Column(name='TOTAL_BANDWIDTH', format='1E',\
    unit='HZ', array=np.zeros(1,dtype='float32')))
  
  c.append(pf.Column(name='SIDEBAND', format='1J',\
    array=np.zeros(1,dtype='int32')))
  
  #c.append(pf.Column(name='BB_CHAN',  format='1J',\
  #  array=np.zeros(1,dtype='int32')))
  

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  cards = generateCards('headers/frequency.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)
    
  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)  
    
  return tblhdu
  
def make_bandpass():
  """
  Creates a vanilla BANDPASS table HDU
  Table is built with the following columns:
  
  BANDPASS table data
  --------------------

  TIME: Difference of bandpass table time int center time and
        RDATE 0 hours
  TIME_INTERVAL: Bandpass table time interval width
  SOURCE_ID:  Source ID number
  ANTENNA_NO: Antenna ID number for station
  ARRAY:      Array ID number
  FREQID:     Frequency setup ID number (should match ANTENNA)
  BANDWIDTH:  Frequency band width described by bandpass
  BAND_FREQ:  Frequency band base offset
  REFANT_1:   Reference antenna ID number
  BREAL_1:    Bandpass response real componet
  BIMAG_1:    Bandpass response imaginary component
  
  """
  c = []
  
  c.append(pf.Column(name='TIME', format='1D',\
   unit='DAYS', array=np.zeros(1,dtype='float64')))
   
  c.append(pf.Column(name='TIME_INTERVAL', format='1E',\
   unit='DAYS',array=np.zeros(1,dtype='float32')))
   
  c.append(pf.Column(name='SOURCE_ID', format='1J',\
    array=np.zeros(1,dtype='int32')))
    
  c.append(pf.Column(name='ANTENNA_NO',format='1J',\
    array=np.zeros(1,dtype='int32')))
    
  c.append(pf.Column(name='ARRAY',     format='1J',\
    array=np.zeros(1,dtype='int32')))
    
  c.append(pf.Column(name='FREQID',    format='1J',\
    array=np.zeros(1,dtype='int32')))
    
  c.append(pf.Column(name='BANDWIDTH', format='1E',\
    unit='HZ', array=np.zeros(1,dtype='float32')))
    
  c.append(pf.Column(name='BAND_FREQ', format='1D',\
   unit='HZ', array=np.zeros(1,dtype='float64')))
   
  c.append(pf.Column(name='REFANT_1',  format='1J',\
    array=np.zeros(1,dtype='int32')))
    
  c.append(pf.Column(name='BREAL_1',  format='1024E',\
    array=np.zeros(1,dtype='1024float32')))
    
  c.append(pf.Column(name='BIMAG_1',  format='1024E',\
    array=np.zeros(1,dtype='1024float32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  cards = generateCards('headers/bandpass.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)  
    
  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)  
    
  return tblhdu  

def make_source():
    """
    Creates a vanilla SOURCE table HDU
    Table is built with the following columns:

    SOURCE table data
    --------------------
    SOURCE_ID Source ID number
    SOURCE    Source name
    QUAL      Source qualifier number.
    CALCODE   Source calibrator code. 
    FREQID    Source frequency ID
    IFLUX     Source I flux density
    QFLUX     Source Q flux density
    UFLUX     Source U flux density
    VFLUX     SourceV flux density
    ALPHA     Source spectral index
    FREQOFF   Source frequency offset
    RAEPO     Source J2000 equatorial position RA coordinate
    DECPO     Source J2000 equatorial position DEC coordinate
    EQUINOX   Mean Equinox
    RAAPP     Source apparent equatorial position RA coordinate
    DECAPP    Source apparent equatorial position DEC coordinate
    SYSVEL    Systematic velocity.
    VELTYP    Systematic velocity reference frame.
    VELDEF    Systematic velocity convention.
    RESTFREQ  Line rest frequency.
    PMRA      Source proper motion RA coordinate
    PMDEC     Source proper motion DEC coordinate
    PARALLAX  Source parallax. 

    """

    c=[]

    c.append(pf.Column(name='SOURCE_ID',    format='1J',\
      array=np.zeros(1,dtype='int32')))
      
    c.append(pf.Column(name='SOURCE',   format='16A',\
      array=np.zeros(1,dtype='16a')))
      
    c.append(pf.Column(name='QUAL',     format='1J',\
      array=np.zeros(1,dtype='int32')))
      
    c.append(pf.Column(name='CALCODE',  format='4A',\
      array=np.zeros(1,dtype='4a')))
      
    c.append(pf.Column(name='FREQID',   format='1J',\
      array=np.zeros(1,dtype='int32')))
      
    c.append(pf.Column(name='IFLUX',    format='1E',\
      array=np.zeros(1,dtype='float32')))
    
    c.append(pf.Column(name='QFLUX',    format='1E',\
      array=np.zeros(1,dtype='float32')))
    
    c.append(pf.Column(name='UFLUX',    format='1E',\
      array=np.zeros(1,dtype='float32')))
    
    c.append(pf.Column(name='VFLUX',    format='1E',\
      array=np.zeros(1,dtype='float32')))
    
    c.append(pf.Column(name='ALPHA',    format='1E',\
      array=np.zeros(1,dtype='float32')))
    
    c.append(pf.Column(name='FREQOFF',  format='1E',
      array=np.zeros(1,dtype='float32')))
    
    c.append(pf.Column(name='RAEPO',    format='1D',\
     unit='DEGREES', array=np.zeros(1,dtype='float64')))
    
    c.append(pf.Column(name='DECEPO',    format='1D',\
     unit='DEGREES', array=np.zeros(1, dtype='float64')))
    
    c.append(pf.Column(name='EQUINOX',    format='8A',\
      array=np.zeros(1,dtype='8a')))
      
    c.append(pf.Column(name='RAAPP',    format='1D',\
     unit='DEGREES', array=np.zeros(1,dtype='float64')))
     
    c.append(pf.Column(name='DECAPP',   format='1D',\
     unit='DEGREES', array=np.zeros(1,dtype='float64')))
    
    c.append(pf.Column(name='SYSVEL',   format='1D',\
      unit='METERS/SEC', array=np.zeros(1,dtype='float64')))
    
    c.append(pf.Column(name='VELTYP',   format='8A',\
      array=np.zeros(1,dtype='8a')))
    
    c.append(pf.Column(name='VELDEF',   format='8A',\
      array=np.zeros(1,dtype='8a')))
    
    c.append(pf.Column(name='RESTFREQ', format='1D',\
     unit='HZ', array=np.zeros(1,dtype='float64')))
    
    c.append(pf.Column(name='PMRA',     format='1D',\
     unit='DEGREES/DAY', array=np.zeros(1,dtype='float64')))
    
    c.append(pf.Column(name='PMDEC',    format='1D',\
     unit='DEGREES/DAY', array=np.zeros(1,dtype='float64')))
    
    c.append(pf.Column(name='PARALLAX', format='1E',\
     unit='ARCSEC', array=np.zeros(1,dtype='float32')))

    coldefs = pf.ColDefs(c)
    tblhdu = pf.new_table(coldefs)

    cards = generateCards('headers/source.head')
    for card in cards:
      tblhdu.header.update(card.key, card.value, card.comment)

    # Override with common values
    cards = generateCards('headers/common.head')
    for card in cards:
      tblhdu.header.update(card.key, card.value, card.comment)
        
    return tblhdu

def make_uv_data(t_len, bl_len):
  """
  Creates a vanilla UV_DATA table HDU
  Table is built with the following columns:
  
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
  
  """
  c = []                
  
  numrows = t_len*bl_len
                                          
  c.append(pf.Column(name='UU',        format='1E',\
    unit='SECONDS', array=np.zeros(numrows,dtype='float32')))
   
  c.append(pf.Column(name='VV',        format='1E',\
    unit='SECONDS', array=np.zeros(numrows,dtype='float32')))
   
  c.append(pf.Column(name='WW',        format='1E',\
    unit='SECONDS', array=np.zeros(numrows,dtype='float32')))
   
  c.append(pf.Column(name='DATE',      format='1D',\
    unit='DAYS', array=np.zeros(numrows,dtype='float64')))
   
  c.append(pf.Column(name='TIME',      format='1D',\
    unit='DAYS', array=np.zeros(numrows,dtype='float64')))
   
  c.append(pf.Column(name='BASELINE',  format='1J',\
    array=np.zeros(numrows,dtype='int')))

  c.append(pf.Column(name='SOURCE',    format='1J',\
    array=np.zeros(numrows,dtype='int32')))
    
  c.append(pf.Column(name='FREQID',    format='1J',\
    array=np.zeros(numrows,dtype='int32')))
    
  c.append(pf.Column(name='INTTIM',    format='1E',\
    unit='SECONDS', array=np.zeros(numrows,dtype='float32')))
    
  c.append(pf.Column(name='WEIGHT',    format='2048E',\
    array=np.zeros(numrows,dtype='2048float32')))
    
  c.append(pf.Column(name='FLUX',      format='2048E',\
    unit='UNCALIB', array=np.zeros(numrows,dtype='2048float32')))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  cards = generateCards('headers/uv_data.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)
  
  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)  
        
  return tblhdu

def make_interferometer_model():
  """
  Creates a vanilla INTERFEROMETER_MODEL table HDU.
  Note this table is optional, and is not included in Medicina FITS IDI
  Table is built with the following columns:
  
  INTERFEROMETER_MODEL table data
  --------------------------------
  
  TIME          Starting time of interval
  TIME_INTERVAL Duration of interval
  SOURCE_ID     Source ID number
  ANTENNA_NO    Antenna number
  ARRAY         Array number
  FREQID        Frequency setup number
  I.FAR.ROT     Ionospheric Faraday rotation
  FREQ_VAR      Time-variable frequency offsets
  PDELAY_1      Phase delay polynomials for polarization 1
  GDELAY_1      Group delay polynomials for polarization 1
  PRATE_1       Phase delay rate polynomials for polarization 1
  GRATE_1       Group rate polynomials for polarization 1
  DISP_1        Dispersive delay for polarization 1 at 1m wavelength
  DDISP_1       Rate of change of dispersive del for pol 1 at 1m
  
  """
  
  c = []
                                        
  c.append(pf.Column(name='TIME',         format='1D', unit='DAYS'))
  c.append(pf.Column(name='TIME_INTERVAL',format='1E', unit='DAYS'))
  c.append(pf.Column(name='SOURCE_ID',    format='1J'))
  c.append(pf.Column(name='ANTENNA_NO',   format='1J'))
  c.append(pf.Column(name='ARRAY',        format='1J'))
  c.append(pf.Column(name='FREQID',       format='1J'))
  c.append(pf.Column(name='I.FAR.ROT',    format='1E', unit='RAD/M**2'))
  c.append(pf.Column(name='FREQ.VAR',     format='1E', unit='HZ'))
  c.append(pf.Column(name='PDELAY_1',     format='1E', unit='TURNS'))
  c.append(pf.Column(name='GDELAY_1',     format='1E', unit='SECONDS'))
  c.append(pf.Column(name='PRATE_1',      format='1E', unit='HZ'))
  c.append(pf.Column(name='GRATE_1',      format='1E', unit='SEC/SEC'))
  c.append(pf.Column(name='DISP_1',       format='1E', unit='SECONDS'))
  c.append(pf.Column(name='DDISP_1',      format='1E', unit='SEC/SEC'))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  cards = generateCards('headers/interferometer_model.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment) 
       
  return tblhdu      
                                    
def make_system_temperature():
  """
  Creates a vanilla SYSTEM_TEMPERATURE table HDU
  This is an optional table (we will not include it)
  Table is built with the following columns:
  
  SYSTEM_TEMPERATURE table data
  --------------------------------
  
  TIME          Central time of interval covered
  TIME_INTERVAL Duration of interval
  SOURCE_ID     Source ID number
  ANTENNA_NO    Antenna number
  ARRAY         Array number
  FREQID        Frequency setup number
  TSYS_1        System temperatures for polarization 1
  TANT_1        Antenna temperatures for polarization 1
  
  """
  c = []
  
  c.append(pf.Column(name='TIME',           format='1D', unit='DAYS'))
  c.append(pf.Column(name='TIME_INTERVAL',  format='1E', unit='DAYS'))
  c.append(pf.Column(name='SOURCE_ID',      format='1J'))
  c.append(pf.Column(name='ANTENNA_NO',     format='1J'))
  c.append(pf.Column(name='ARRAY',          format='1J'))
  c.append(pf.Column(name='FREQID',         format='1J'))
  c.append(pf.Column(name='TSYS_1',         format='1E', unit='KELVIN'))
  c.append(pf.Column(name='TANT_1',         format='1E', unit='KELVIN'))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  cards = generateCards('headers/system_temperature.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)
  
  return tblhdu   

def make_gain_curve():
  """
  Creates a vanilla GAIN_CURVE table HDU
  This is an optional table (we will not include it)
  Table is built with the following columns:
  
  GAIN_CURVE table data
  --------------------------------
  
  ANTENNA_NO  Antenna number
  ARRAY       Array number
  FREQID      Frequency setup number
  TYPE_1      Gain curve types for polarization 1
  NTERM_1     Numbers of terms or entries for polarization 1
  X_TYP_1     x value types for polarization 1
  Y_TYP_1     y value types for polarization 1
  X_VAL_1     x values for polarization 1
  Y_VAL_1     y values for polarization 1
  GAIN_1      Relative gain values for polarization 1
  SENS_1      Sensitivities for polarization 1
  
  """

  c = []
  
  c.append(pf.Column(name='ANTENNA_NO',  format='1J'))
  c.append(pf.Column(name='ARRAY',       format='1J'))
  c.append(pf.Column(name='FREQID',      format='1J'))
  c.append(pf.Column(name='TYPE_1',      format='1J'))
  c.append(pf.Column(name='NTERM_1',     format='1J'))
  c.append(pf.Column(name='X_TYP_1',     format='1J'))
  c.append(pf.Column(name='Y_TYP_1',     format='1J'))
  c.append(pf.Column(name='X_VAL_1',     format='1J'))
  c.append(pf.Column(name='Y_VAL_1',     format='1J'))
  c.append(pf.Column(name='GAIN_1',      format='1J'))
  c.append(pf.Column(name='SENS_1',      format='1J', unit='K/JY'))
  
  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  cards = generateCards('headers/gain_curve.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  return tblhdu

def make_phase_cal():
  """
  Creates a vanilla PHASE-CAL table HDU
  This is an optional table (we will not include it)
  
  Table is built with the following columns:

  PHASE-CAL table data
  --------------------------------

  TIME          Central time of interval covered
  TIME_INTERVAL Duration of interval
  SOURCE_ID     Source ID number
  ANTENNA_NO    Antenna number
  ARRAY         Array number
  FREQID        Frequency setup number
  CABLE_CAL     Cable calibration measurement
  STATE_1       State counts for polarization 1
  PC_FREQ_1     Phase cal tone frequencies for polarization 1
  PC_REAL_1     real parts of phase-cal measurements for pol 1
  PC_IMAG_1     imaginary parts of phasecal measurements for pol 1
  PC_RATE_1     phase-cal rates for polarization 1

  """

  c = []
                                        
  c.append(pf.Column(name='TIME',          format='1D', unit='DAYS'))
  c.append(pf.Column(name='TIME_INTERVAL', format='1E', unit='DAYS'))
  c.append(pf.Column(name='SOURCE_ID',     format='1J'))
  c.append(pf.Column(name='ANTENNA_NO',    format='1J'))
  c.append(pf.Column(name='ARRAY',         format='1J'))
  c.append(pf.Column(name='FREQID',        format='1J'))
  c.append(pf.Column(name='CABLE_CAL',     format='1E', unit='SECONDS'))
  c.append(pf.Column(name='STATE_1',       format='1J', unit='PERCENT'))
  c.append(pf.Column(name='PC_FREQ_1',     format='1J', unit='HZ'))
  c.append(pf.Column(name='PC_REAL_1',     format='1J'))
  c.append(pf.Column(name='PC_IMAG_1',     format='1J'))
  c.append(pf.Column(name='PC_RATE_1',     format='1J', unit='SEC/SEC'))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)

  cards = generateCards('headers/phase_cal.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)

  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)
    
  return tblhdu

def make_flag():
  """
  Creates a vanilla FLAGL table HDU
  Table is built with the following columns:

  FLAG table data
  --------------------------------

  SOURCE_ID Source ID number
  ARRAY     Array number
  ANTS      Antenna numbers
  FREQID    Frequency setup number
  TIMERANG  Time range
  BANDS     Band flags
  CHANS     Channel range
  PFLAGS    Polarization flags
  REASON    Reason for flag
  SEVERITY  Severity code

  """

  c = []
    
  c.append(pf.Column(name='SOURCE_ID', format='1J'))
  c.append(pf.Column(name='ARRAY',     format='1J'))
  c.append(pf.Column(name='ANTS',      format='2J'))
  c.append(pf.Column(name='FREQID',    format='1J'))
  c.append(pf.Column(name='TIMERANG',  format='2E', unit='DAYS'))
  c.append(pf.Column(name='BANDS',     format='1J'))
  c.append(pf.Column(name='CHANS',     format='2J'))
  c.append(pf.Column(name='PFLAGS',    format='4J'))
  c.append(pf.Column(name='REASON',    format='24A'))
  c.append(pf.Column(name='SEVERITY',  format='1J'))

  coldefs = pf.ColDefs(c)
  tblhdu = pf.new_table(coldefs)
  
  cards = generateCards('headers/flag.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)
  
  # Override with common values
  cards = generateCards('headers/common.head')
  for card in cards:
    tblhdu.header.update(card.key, card.value, card.comment)  
    
  return tblhdu
  
def config_antenna(tbl):
  """
  Configures the antenna table with some default values
  """

  antenna = tbl.data
  for i in range(0,tbl.data.size):
    
    antenna[i]['ANNAME'] = 'MED_%i'%i
    antenna[i]['ANTENNA_NO'] = i
    antenna[i]['ARRAY'] = 1
    antenna[i]['FREQID'] = 1
    antenna[i]['NO_LEVELS'] = 12
    antenna[i]['POLTYA'] = 'R'
    antenna[i]['POLTYB'] = 'R'
    antenna[i]['POLAA'] = 0
    antenna[i]['POLAB'] = 0
    
    
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
  source['SOURCE'] = sourcename
  source['VELDEF'] = 'RADIO'
  source['VELTYP'] = 'GEOCENTR'
  source['FREQID'] = 1
  source['RAEPO'] = 299.8667
  source['DECEPO'] = 40.7339
  source['EQUINOX'] = 'J2000'
  
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

  frequency['FREQID'] = 1
  frequency['BANDFREQ'] = 0
  frequency['CH_WIDTH'] = 20.0/1024.0
  frequency['TOTAL_BANDWIDTH'] = 20*10**6
  frequency['SIDEBAND'] = 1

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
  
    
     
def main():
  """
  Generate a blank FITS IDI file for use in Medicina BEST-2
  32 element array.
  """

  print('Creating Primary HDU')
  print('------------------------------------\n')
  
  # Make a new blank FITS HDU
  hdu = pf.PrimaryHDU()
  
  # Primary HDU is generated solely from primary.head file
  filename = 'headers/primary.head'
  cards = generateCards(filename)

  for card in cards:
    hdu.header.update(card.key, card.value, card.comment)
  
  hdu.verify() # Will raise a warning if there's an issue  
  print hdu.header.ascardlist()
  print('\n')

  # Go through and generate required tables
  print('Creating ARRAY_GEOMETRY')
  print('------------------------------------')  
  tbl_array_geometry = make_array_geometry()
  tbl_array_geometry = config_array_geometry(tbl_array_geometry)
  #print tbl_array_geometry.header.ascardlist()
  print('\n')
  
  print('Creating FREQUENCY')
  print('------------------------------------')
  tbl_frequency = make_frequency()
  tbl_frequency = config_frequency(tbl_frequency)
  #print tbl_frequency.header.ascardlist()
  print('\n')

  print('Creating SOURCE')
  print('------------------------------------')
  tbl_source = make_source()
  tbl_source = config_source(tbl_source)
  #print tbl_source.header.ascardlist()
  print('\n')

  print('Creating ANTENNA')
  print('------------------------------------')
  tbl_antenna = make_antenna()
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
  # print('Creating SYSTEM_TEMPERATURE')
  # print('------------------------------------')
  # tbl_system_temperature = make_system_temperature()
  # print tbl_system_temperature.header.ascardlist()
  # print('\n')
  
  # Bandpass is optional too
  # print('Creating BANDPASS')
  # print('------------------------------------')
  # tbl_bandpass = make_bandpass()
  # print tbl_bandpass.header.ascardlist()
  # print('\n')
  
  # UV_DATA data - MANDATORY
  print('Creating UV_DATA')
  print('------------------------------------')
  (t_len, bl_len) = 10, 528
  tbl_uv_data = make_uv_data(t_len, bl_len)
  #print tbl_uv_data.header.ascardlist()
  #tbl_uv_data = config_uv_data(tbl_uv_data)
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
              # tbl_system_temperature,
              # tbl_phase_cal,
              tbl_uv_data
              ])
  
  print('Verifying integrity...')            
  hdulist.verify()
  
  
  filename = 'corr.2455676.70269.fits'
  if(os.path.isfile(filename)):
    print('Removing existing file...')
    os.remove(filename)
  print('Writing to file...')
  hdulist.writeto(filename)

  print('Done.')


if __name__ == '__main__':
  main()
  
