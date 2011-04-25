The .head files in this directory are used to generate the key values for each of the required tables for a FITS IDI file. Each line is read by the createFitsIDI.py script, checked for integrity, and then converted into a pyfits card. Once a big list of all the cards has been created, the table header is updated with these values.

These header files shouldn't contain the basic table data structure cards, such as:

XTENSION= 'BINTABLE'           / FITS Binary Table Extension
BITPIX  =                    8 /
NAXIS   =                    2 /
NAXIS1  =                  484 /
NAXIS2  =                  241 /
PCOUNT  =                    0 /
GCOUNT  =                    1 /
TFIELDS =                   17 /

TTYPE1  = 'TIME    '           / time of center of interval
TFORM1  = '1D      '           /
TUNIT1  = 'DAYS    '           /
TTYPE2  = 'TIME_INTERVAL'      / time span of datum
TFORM2  = '1E      '           /
TUNIT2  = 'DAYS    '           /

That is, you should REMOVE THIS TYPE OF STUFF from .head files.