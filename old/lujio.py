import os
import luafuncs as lf
try:
    import numpy 
except:
    pass

# abspath = os.path.abspath('./') + '/'

dicLua = {}
dicLua['number'] = 'element'
dicLua['string'] = 'element'
dicLua['table']  = 'list'

# def _get_var_name(assignment, main_var=None):
#     """
#     function to grab variable name
#     """
#     try:
#         mvar = [key for key, val in main_var.items() if val==assignment][0]
#         return mvar
#     except:
#         print('Error')

class LujIO(object):
    """
    Documentation
    """
    
    def __init__(self, command, python_obj=False, lua_obj=False, pl_type = 'auto', lp_type= 'auto', **kwargs):
        """
        
        """
        self.abspath = os.path.abspath('./') + '/'
        
        if python_obj:
            self.python_obj = python_obj
            # self.python_obj_name = _get_var_name(python_obj, vars())
            self.python_obj_name = 'py_obj'
            
        if lua_obj:
            self.lua_obj_name = lua_obj
        
        self.command = command
        
        # Need to chance in and out to pl or lp (python-lua, lua-python)
        self.pl_type = pl_type
        self.lp_type = lp_type
        
        # Setup dictionary for add_begin and add_end to automate in and out reading/writing.
        self.beginDic = {}
        self.endDic = {}
        self.beginDic['element'] = lf.grab_func('numpy_in_lua') + lf.grab_func('string_split') + lf.grab_func('string_join') \
                        + 'data = io.open("' + self.abspath + 'data.txt","r")\n' \
                        + self.python_obj_name + ' = data:read("*all")\ndata:close()\n'
        
        self.beginDic['list'] = lf.grab_func('numpy_in_lua') + lf.grab_func('string_split') \
                        + lf.grab_func('string_join') \
                        + 'data = io.open("' + self.abspath + 'data.txt","r")\n' \
                        + self.python_obj_name + ' = data:read("*all")\ndata:close()\n'\
                        + self.python_obj_name + ' = ' + self.python_obj_name + ':gsub("%[","")\n'\
                        + self.python_obj_name + ' = ' + self.python_obj_name + ':gsub("%]","")\n'\
                        + self.python_obj_name + ' = split(' + self.python_obj_name + ',",")\n'
        
        self.beginDic['numpy_array'] = lf.grab_func('numpy_in_lua') + lf.grab_func('string_split') + lf.grab_func('string_join') + lf.grab_func('numpy_parse')\
                        + 'data = io.open("' + self.abspath + 'data.txt","r")\n'\
                        + self.python_obj_name + ' = data:read("*all")\ndata:close()\n'\
                        + self.python_obj_name + '= numpy_parser(' + self.python_obj_name + ')\n'
        
        self.endDic['lua_type'] = '\nout_type = io.open("' + self.abspath + 'out_type.txt","w")\n' \
                        +'out_type:write(type(' + self.lua_obj_name + '))\n' \
                        +'out_type:close()\n'
        
        self.endDic['output_func'] = '\nfunction output(var)\n'\
                        +'if (type(var) == type("str")) or (type(var) == type(1)) then\n'\
                        + 'new_data = io.open("' + self.abspath + 'new_data.txt","w")\n'\
                        + 'new_data:write(' + self.lua_obj_name + ')\n'\
                        + 'new_data:close()\nend'\
                        + '\nif (type(var) == type({1,2})) then\n'\
                        + self.lua_obj_name +'= join('+self.lua_obj_name+')\n'\
                        + 'new_data = io.open("' + self.abspath + 'new_data.txt","w")\n'\
                        + 'new_data:write(' + self.lua_obj_name + ')\nnew_data:close()\n'\
                        + '\nend \nend\n'\
                        + 'output(' + self.lua_obj_name + ')'
        
        self.endDic['element'] = '\nnew_data = io.open("' + self.abspath + 'new_data.txt","w")\n' \
                        + 'new_data:write(' + self.lua_obj_name + ')\nnew_data:close()'
        
        self.endDic['list'] = self.lua_obj_name +'= join('+self.lua_obj_name+')\n' \
                        + 'new_data = io.open("' + self.abspath + 'new_data.txt","w")\n' \
                        + 'new_data:write(' + self.lua_obj_name + ')\nnew_data:close()\n'
    
            
    def _write_command(self):
        """
        
        """
        # print('executing _write_command')
        if (self.python_type == int) or (self.python_type == float) or (self.python_type == list) or (self.python_type == dict):
            self.command = self.beginDic[self.dic_type] + self.command \
                            + self.endDic['lua_type'] + self.endDic['output_func']
        
        elif (self.python_type == type(numpy.ndarray([]))):
            self.command = self.beginDic[self.dic_type] + self.command \
                            + self.endDic['lua_type'] + self.endDic['output_func']
        
        f = open('command.lua', 'w')
        f.write(self.command)
        f.close()
    
    def _write_string(self):
        """

        """
        # print('executing _write_string')
        if (self.python_type == int) or (self.python_type == float):
            f = open('data.txt','w')
            f.write(str(self.python_obj))
            f.close()
        elif (self.python_type == list) or (self.python_type == dict):
            f = open('data.txt','w')
            # self.python_obj= string.join()
            ### Setup ###
            # Need to make this support NxM dimensions
            f.writelines(str(self.python_obj))
            f.close()
        elif (self.python_type == type(numpy.ndarray([]))):
            numpy.savetxt(self.obj, delimiter = ',')
            # Will need to make a dict for formatting (e.g. integers)
        else:
            print('The data type you are trying to write is not recognized by Luj.')

    
    def _read_string(self):
        """
        """
        # print('executing _read_string')
        if self._lua_type == 'element':
            f = open('new_data.txt','r')
            self._new_data = f.readline()
            f.close()
            # print('_read_string chose element')
            # will have to enter stuff about return format
        elif self._lua_type == 'list':
            try:
                self._new_data = numpy.loadtxt('new_data.txt')
            except:
                f = open('new_data.txt','r')
                self._new_data = f.readlines()
                f.close()
                # print('_read_string chose list')
        else:
            print('something is not working with _read_string')
    
    def _write_binary(self):
        """
        Still testing
        """
        pass
    
    def _read_binary(self):
        """
        Still testing
        """
        pass
    
    def _pl_type(self):
        """
        """
        # print('executing _pl_type')
        self.python_type = type(self.python_obj)
        
        try: 
            if (self.python_type == int) or (self.python_type == float) or (self.python_type == numpy.float):
                self.dic_type = 'element'
                # print('python type is element')
        
            elif self.python_type == list:
                self.dic_type = 'list'
                # print('python type is element')
        
            elif self.python_type == dict:
                self.dic_type = 'dict'
        
            elif self.python_type == type(numpy.ndarray([])):
                self.dic_type = 'numpy_array'
        
        except:
            print 'Data type ' + str(self.python_type) + ' is not recognized by Lua'
            
    
    def _lp_type(self):
        """
        
        """
        # print('executing _lp_type')
        if self.lp_type == 'auto':
            f = open(self.abspath+'out_type.txt','r')
            data = f.readlines()
            try:
                self._lua_type = dicLua[data[0]]
            except:
                print('This Lua type, ' + data[0] + ', is not recognized by Luj')
        
