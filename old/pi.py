from time import time
import random, os
import subprocess as sp
import luj

abspath = os.path.abspath('./') + '/'


# Pure Python
def find_pi(n):
    c = 0
    for i in range(n):
        x = 2. * random.random() - 1.
        y = 2. * random.random() - 1.
        d = x*x + y*y
        if d < 1:
            c += 1
    return 4. * float(c) / float(n)
    
n = 20000000
start = time()
print "pi = %.10f" % find_pi(n)
print "Pure Python in %.3f seconds" % (time() - start)

# Luj

def lua_find_pi(n):
    command = """
    function find_pi(n)
        c = 0
        for i = 0,n do
            x = 2 * math.random() - 1
            y = 2 * math.random() - 1
            d = x*x + y*y
            if d < 1 then
                c = c + 1
            end
        end
        return 4 * c / n
    end
    
    n = py_obj
    pi = find_pi(n)
    """
    
    pi = luj.lua(command, python_obj = n, lua_obj = 'pi', lua_call = 'luajit')
    return float(pi)

start = time()
print "\npi = %.10f" % lua_find_pi(n)
print "Luj with luajit in %.3f seconds" % (time() - start)

# Pure LuaJIT

print('\n')
start = time()
sp.call(['luajit', abspath + 'examples/pi.lua'])
print "Pure luajit with Python call in %.3f seconds" % (time() - start)


