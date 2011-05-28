.. Python FITS IDI documentation master file, created by
   sphinx-quickstart on Thu Apr 28 19:55:01 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 4


Welcome to pyFitsidi
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


About pyFitsidi
~~~~~~~~~~~~~~~

pyFitsidi is a python module that creates FITS IDI files.

pyFitsidi is a collection of functions that create headers and data units that conform to the FITS-IDI convention. It was written primarily to convert data from a CASPER correlator into a format that can be imported into data reduction packages such as AIPS++ and CASA. 

.. figure:: medicina.jpg
  :alt: The Northern Cross, Medicina
  :align: center
  
  The Northern Cross, Medicina, Italy. Photo by G. Foster.




The FITS IDI convention
~~~~~~~~~~~~~~~~~~~~~~~~~

The FITS Interferometry Data Interchange Convention (“FITS-IDI”) is a set of conventions layered upon the standard FITS format to assist in the interchange of data recorded by interferometric telescopes, particularly at radio frequencies and very long baselines.

FITS IDI is a registered convention in the NASA/IAU FITS working group registry, meaning it is defined and documented to "a minimum level of completeness and clarity". FITS IDI files can be read by AIPS, AIPS++ and CASA (although I have only tested with CASA). They are used by the VLBA (Very Long Baseline Array) and JIVE (Joint Institute for VLBI in Europe), among others.

There are a few alternative formats to FITS IDI, such as `Miriad <http://www.atnf.csiro.au/computing/software/miriad/>`_ FITS files, UVFITS files, and `Measurement Sets <http://casa.nrao.edu/docs/userman/UserManse6.html>`_ (MS). Miriad is getting a little long in the tooth, UVFITS is not very well documented, and Measurement Sets are a bit of a pain to create -- plus, a MS isn't a FITS file, so it can't be read by FITS readers. 

Much more info on the FITS IDI convention can be found on its `official page
<http://fits.gsfc.nasa.gov/registry/fitsidi.html>`_. If you're not familiar with FITS files, you might also want to look at the actual `FITS definition <http://www.aanda.org/index.php?option=com_article&access=doi&doi=10.1051/0004-6361/201015362&Itemid=129>`_. Finally, there are useful FITS resources at the `NASA FITS website <http://fits.gsfc.nasa.gov/fits_home.html>`_.

Prerequisites
~~~~~~~~~~~~~~~~

The actual reading/writing of FITS files is done by the `PyFITS <http://www.stsci.edu/resources/software_hardware/pyfits>`_ package. You'll also need `numpy <http://numpy.scipy.org/>`_ for array handling and `lxml <http://lxml.de/>`_ for parsing config XML files.

In the file createMedicinaFITS.py, we make use of `pyEphem <http://rhodesmill.org/pyephem/>`_ for astronomical calculations, and `pyTables <http://www.pytables.org/moin>`_ for HDF5 file I/O. Yo 

Example Usage
~~~~~~~~~~~~~

A simple example of how to use pyFitsidi.py can be found in the createFitsIDI.py:

>>> """
... createFitsIDI.py
... =============
... 
... Creates a basic FITS IDI file, with headers created from an XML configuration file.
... 
... Created by Danny Price on 2011-04-20.
... Copyright (c) 2011 The University of Oxford. All rights reserved.
... 
... """
... 
... # Required modules
... import sys, os
... import pyfits as pf, numpy as np
... 
... # import modules from this package
... from pyFitsidi import *
... 
... def main():
...   """
...   Generate a blank FITS IDI file.
...   """
...   
...   # What are the filenames for our datasets?
...   fitsfile = 'blank.fits'
...   config   = 'config/config.xml'
...   
...   # Make a new blank FITS HDU
...   print('Creating Primary HDU')
...   print('------------------------------------\n')
...   hdu = make_primary(config)
...   print hdu.header.ascardlist()
...   
...   # Go through and generate required tables
...   print('\nCreating ARRAY_GEOMETRY')
...   print('------------------------------------')
...   tbl_array_geometry = make_array_geometry(config=config, num_rows=32)
...   print tbl_array_geometry.header.ascardlist()
... 
...   print('\nCreating FREQUENCY')
...   print('------------------------------------')
...   tbl_frequency = make_frequency(config=config, num_rows=1)
...   print tbl_frequency.header.ascardlist()
... 
...   print('\nCreating SOURCE')
...   print('------------------------------------')
...   tbl_source = make_source(config=config, num_rows=1)
...   print tbl_source.header.ascardlist()
... 
...   print('\nCreating ANTENNA')
...   print('------------------------------------')
...   tbl_antenna = make_antenna(config=config, num_rows=32)
...   print tbl_antenna.header.ascardlist()
... 
...   print('\nCreating UV_DATA')
...   print('------------------------------------')
...   # Number of rows req. depends on num. time dumps and num. of baselines
...   # Once you have data, it would be worth setting these dimensions automatically
...   # For now, we're hard-wiring in 1 time dump, 528 baselines (32 element array)
...   (t_len, bl_len) = (1,528) 
...   tbl_uv_data = make_uv_data(config=config, num_rows=t_len*bl_len)
...   print tbl_antenna.header.ascardlist()
... 
...   print('\nCreating HDU list')
...   print('------------------------------------')  
...   hdulist = pf.HDUList(
...               [hdu, 
...               tbl_array_geometry,
...               tbl_frequency,
...               tbl_antenna,
...               tbl_source, 
...               tbl_uv_data
...               ])
...   
...   print('\nVerifying integrity...')            
...   hdulist.verify()
...   
...   if(os.path.isfile(fitsfile)):
...     print('Removing existing file %s...')%fitsfile
...     os.remove(fitsfile)
...   print('Writing to file %s...')%fitsfile
...   hdulist.writeto(fitsfile)
... 
...   print('Done.')
... 
... 
... if __name__ == '__main__':
...   main()

A more complicated example is shown in createMedicinaFITS.py. In this file, a complete FITS IDI file is generated from an XML config file and a HDF5 data file. While the XML and HDF5 data are specific to the Medicina BEST-2 telescope, this file could be adapted as required.

In createMedicinaFITS.py, only the mandatory binary tables are created: array_geometry, antenna, frequency, source and uv_data.

Module Documentation
~~~~~~~~~~~~~~~~~~~~

.. automodule:: pyFitsidi
    :members:

.. automodule:: astroCoords
    :members:

