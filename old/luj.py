import os
import subprocess as sp
from lujio import LujIO

# abspath = os.path.abspath('./') + '/'

def lua(command, python_obj = False, lua_obj = False, format = 'text', lua_call = 'lua', 
                pl_type = 'auto', lp_type= 'auto', **kwargs):
    abspath = os.path.abspath('./') + '/'
    setup = LujIO(command, python_obj, lua_obj)
    setup._pl_type()
    # _type = setup.type
    if format == 'text':
        setup._write_string()
        setup._write_command()
        sp.call([lua_call, abspath+'command.lua'])
        setup._lp_type()
        setup._read_string()
    elif format == 'binary':
        pass
    
    # os.call(['rm',abspath+'command.lua',abspath+'data.txt',abspath+'command.lua'])
    return setup._new_data

