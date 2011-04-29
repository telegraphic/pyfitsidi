# encoding: utf-8
"""
medicina_uvw.py

Locations of the Medicina antennas

Created by Danny Price on 2011-04-25.
Copyright (c) 2011 The University of Oxford. All rights reserved.
"""

import ephem
import numpy as np
import sys, os, datetime

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

def main():
  """docstring for main"""
  # Stop. Hammer time.
  now = datetime.datetime.now()
  
  # We are at Medicina, Italy
  (latitude, longitude, elevation) = ('44:31:24.88', '11:38:45.56', 28) 
  
  # Let's make ourselves an Array (pyEphem observer)
  medicina = Array(lat=latitude, long=longitude,elev=elevation,date=now)
  
  print medicina
  
  # http://www.oc.nps.edu/oc2902w/coord/llhxyz.htm
  # ECEF from Latitude,Longitude, Height (ellipsoidal)
  # X : 4461.122   km
  # Y : 919.469   km
  # Z : 4449.776   km
  
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
  xyz_m = xyz_ns * 10**-9 * light_speed
  
  print xyz_m

if __name__ == '__main__':
  main()

