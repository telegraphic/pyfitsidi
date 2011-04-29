# encoding: utf-8
"""
Interferometer.py

Created by Danny Price on 2010-09-17.
Copyright (c) 2010 The University of Oxford. All rights reserved.
"""

import sys, os, datetime, pylab, matplotlib 
import ephem
import numpy as np
import aipy as ap

global earth_radius, light_speed, pi, freq
earth_radius = 6371 * 10**3     # Earth's radius
light_speed = 299792458         # Speed of light
pi = np.pi                      # Pi
freq = 10**9                    # 1 GHz

class Antenna(ephem.Observer):
    """ An antenna object, the thing that picks up radiation.
        Based on pyEphem's Observer class
    """
    def __init__(self, lat, long, elevation,date):
        super(Antenna, self).__init__()
        self.lat = lat
        self.long = long
        self.elevation = elevation
        self.date = date
    
    def update(self, date):
        """Update antenna with a new datetime"""
        self.date = date
        

class Interferometer(object):
    """ An interferometer object, which is comprised of two antennas.
        A loose extension of pyEphem's Observer class.
        ant1: an Antenna object
        ant2: an Antenna object
    """
    def __init__(self, ant1, ant2, pointing=(0,0,0)):
        super(Interferometer, self).__init__()
        self.ant1 = ant1
        self.ant2 = ant2
        self.pointing = pointing
        

    def point(self, x,y,z):
        """ Set the pointing angle of interferometer, (x, y, z)
            ideally should be normalised.
        """
        self.pointing = (x, y, z)
        return self.pointing
        
    def gcd(self):
        """ Uses Haverside formula to calculate great circle distances (GCD)
            between two points on the Earth's surface (i.e. baseline length).
            http://www.movable-type.co.uk/scripts/latlong.html
            Returns a distance in metres (m), accepts radians
        """
        
        lat1, long1 = self.ant1.lat, self.ant1.long
        lat2, long2 = self.ant2.lat, self.ant2.long
        
        dLat = lat1 - lat2
        dLong = long1 - long2
        a = np.sin(dLat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dLong/2)**2
        c = 2* np.arctan2(np.sqrt(a), np.sqrt(1-a))
        d = earth_radius*c
        return d
    
    def baseline(self):
        """ Uses simple trigonometry to figure out the direct distance 
            between two points of lat/long, (accepts radians)
        """
        lat1, long1, elev1 = self.ant1.lat, self.ant1.long, self.ant1.elev
        lat2, long2, elev2 = self.ant2.lat, self.ant2.long, self.ant2.elev
        dLat = lat1 - lat2
        dLong = long1 - long2
        dElev = elev1 - elev2
        
        x = 2* earth_radius * np.sin(dLat/2)
        y = 2* earth_radius * np.sin(dLong/2)
        z = 2* earth_radius * np.sin(dElev/2)
        return (x,y,z)
        
    
    def pathDelay(self):
        """Returns the geometric delay between your two antennas, in s"""
        delay = np.dot(self.baseline(),self.pointing)
        return delay / light_speed
    
    def update(self,date):
        """Update interferometer object with new datetime"""
        self.ant1.update(date)
        self.ant2.update(date)

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

# Helper functions

def cart2pol(x,y,z):
    """ Convert 3D cartesian coords into spherical polar
        Outputs radian values
    """
    rr = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(z/sqrt(x**2+y**2+z**2))
    phi = np.arctan2(y,x)
    return (rr,theta,phi)

def pol2cart(rr,theta,phi):
    """ Convert spherical polar into cartesian coords
        Accepts radian values
    """
    x = rr * np.sin(theta) * np.cos(phi)
    y = rr * np.sin(theta) * np.sin(phi)
    z = rr * np.cos(theta)
    return (x,y,z)

def altaz2pol(alt,az):
    """ Convert altitude/azimuth coords into spherical polar
        Accepts radian values
    """
    # Zenith is 90 degrees from North, not at zero degrees...
    theta = alt-np.pi/2
    phi = az
    
    if theta > np.pi: 
        print "Warning: Alt is larger than 180 degrees, invalid pointing"
    if phi > 2*np.pi:
        print "Warning: Azimuth is larger than 360 degrees, invalid pointing"
    
    return (1,theta,phi)

def altaz2cart(alt,az):
    """ Convert altitude/azimuth coords into cartesian coords
        Accepts radian values
    """
    (rr,theta,phi) = altaz2pol(alt,az)
    (x,y,z)      = pol2cart(rr,theta,phi)
    return (x,y,z)

def normalise(x,y,z):
    """Normalises a 3D vector to have length 1"""
    norm = 1/sqrt(x**2+y**2+z**2)
    return norm*(x,y,z)

def plot(data,title='',xtitle='',ytitle=''):
    """"A super simple plotter"""
    pylab.figure(num=1,figsize=(10,10))
    pylab.plot(data)
    pylab.title(title)
    pylab.xlabel(xtitle)
    pylab.ylabel(ytitle)
    pylab.ioff()
    pylab.show()
    #pylab.draw()

def main():
    
    # Stop. Hammer time.
    now = datetime.datetime.now()
    
    # To make ourselves an interferometer, let's put
    # one antenna in University Parks, the other in Christchurch Meadow
    # This is about 1.3km apart, which should be good for now.
    # http://www.getlatlon.com/
    parks_lat, parks_long   = np.deg2rad(51.761744383827),np.deg2rad(-1.2554454803466)
    meadow_lat, meadow_long = np.deg2rad(51.75006899810), np.deg2rad(-1.2514328956604)
    #meadow_lat, meadow_long = np.deg2rad(51.7618), np.deg2rad(-1.2554454803466)
    
    ant1 = Antenna(lat=parks_lat, long=parks_long,elevation=0,date=now)
    ant2 = Antenna(lat=meadow_lat, long=meadow_long,elevation=0,date=now)
    
    # We're now ready to make an interferometer object
    dpad = Interferometer(ant1,ant2)
    
    # First test: how long is the baseline?
    (x,y,z) = dpad.baseline()
    print "Interferometer baseline setup:"
    print "Baseline: (%dm,%dm,%dm)"%(x,y,z)
    print "Direct distance: %dm"%(np.sqrt(x**2 + y**2 + z**2))
    print "Great circle distance: %dm"%dpad.gcd()
    

    # Next on the agenda is finding the geometric delay between antennas
    # For a given pointing angle. Note that the pointing angle may not be
    # equivalent to the location of a source (there will be many)
    
    # Zenith is (alt,az) =(90,0)
    (alt, az) = np.deg2rad((91,1))
    (rr,theta,phi) = altaz2pol(alt,az)
    (x,y,z)      = pol2cart(rr,theta,phi)
    print "\nInterferometer pointing centre:"
    print "Alt-az: \t %f,%f"%(alt,az)
    print "Spherical: \t %f,%f,%f"%(rr,theta,phi)
    print "Cartesian: \t %f,%f,%f"%(x,y,z)
    
    # Point our array to a position in the sky
    dpad.point(x,y,z)
    print "Resulting geometric delay: %fns"%(dpad.pathDelay() * 10**9)

    # Now it's time for a real source
    CasA = makeSource(
        name="CasA",
        ra='23:23:26',
        dec='58:48',
        flux='2720'
    )

    print "\nSource name: %s"%CasA.name
    CasA.compute(now)
    print "ra: %s, dec: %s"%(CasA.ra, CasA.dec)
    
    # So where do we need to point our array?
    CasA.compute(ant1)
    print "Antenna 1 pointing: \nAlt: %s, Az: %s"%(CasA.alt, CasA.az)
    CasA.compute(ant2)
    print "Antenna 2 pointing: \nAlt: %s, Az: %s"%(CasA.alt, CasA.az)
    
    # Choosing the first antenna as a reference location, we continue
    CasA.compute(ant1)
    (x,y,z) = altaz2cart(CasA.alt,CasA.az)
    dpad.point(x,y,z)
    print "Resulting geometric delay: %fns"%(dpad.pathDelay() * 10**9)
    
    # The geometric delay will change over time, to see this,
    # Let's look at CasA with our Interferometer for 24 hours
    data =[]
    bday = datetime.datetime(1985,10,10,12,30)
    for i in range(0,48):
        diff = datetime.timedelta(minutes=30*i)
        ant1 = Antenna(lat=parks_lat, long=parks_long,elevation=0,date=bday+diff)
        CasA.compute(ant1)
        (x,y,z) = altaz2cart(CasA.alt,CasA.az)
        dpad.point(x,y,z)
        data.append(dpad.pathDelay() * 10**9)
    
    # Plotting the data to see the baseline length changing
    plot(
        data,
        title='Geometric delay for CasA over 24 hours',
        xtitle='Time sample (-)',
        ytitle='Geometric delay (ns)'
        )

    # The geometric delay will change over time, to see this,
    # Let's look at CasA with our Interferometer for 24 hours
    fringes = []
    bday = datetime.datetime(1985,10,10,12,30)
    for i in range(0,1000):
        # Update interferometer time
        diff = datetime.timedelta(minutes=i)
        dpad.update(date=bday+diff)
        
        # Compute pointing direction
        CasA.compute(dpad.ant1)
        (x,y,z) = altaz2cart(CasA.alt,CasA.az)
        dpad.point(x,y,z)
        
        # Compute fringe function (F)
        fringes.append(np.cos(2*pi*freq*dpad.pathDelay()))

    # Plotting the fringe function to see fringes over time
    plot(
        fringes,
        title='Fringe function for CasA over 1000mins',
        xtitle='Time sample (-)',
        ytitle='Amplitude'
        )
    
    # Check the baseline is being updated
    bases = []
    for i in range(0,48):
        diff = datetime.timedelta(minutes=30*i)
        dpad.update(date=bday+diff)
        (x,y,z) = dpad.baseline()
        print "Baseline: (%dm,%dm,%dm)"%(x,y,z)

        
        
        
    
    
if __name__ == '__main__':
	main()

