dict_funcs = {}

# Adopted from http://lua-users.org/wiki/SplitJoin
dict_funcs['string_split'] = """
function split(str, pat)
   local t = {}
   local fpat = "(.-)" .. pat
   local last_end = 1
   local s, e, cap = str:find(fpat, 1)
   while s do
      if s ~= 1 or cap ~= "" then
          table.insert(t,cap)
      end
      last_end = e+1
      s, e, cap = str:find(fpat, last_end)
   end
   if last_end <= #str then
      cap = str:sub(last_end)
      table.insert(t, cap)
   end
   return t
end

"""

dict_funcs['numpy_parse'] ="""
function numpy_parser(data)
    tmp1 = split(data,string.char(10))
    tmp2 = {}
    tbl = {}
    for key1, item1 in pairs(tmp1) do
        tmp2 = split(item1,',')
        tbl[key1] = {}
        for key2, item2 in pairs(tmp2) do
            tbl[key1][key2] = item2
        end
    end
    return tbl
end

"""

dict_funcs['numpy_in_lua'] = """
-- Here we have metatable functions that make 
-- tables behave like numpy arrays for division,
-- multiplication, exponents, addition, and 
-- subraction. This is geared for 1 x N arrays
-- and scalars. 

-- You snooze, you lose. Hence, you must use Luj!

numpy = {}
local mt = {}

function len(a)
    if type(a) == type({}) then
        return table.maxn(a)
    else
        error('len works only for tables/arrays')
    end
end

function cases(a,b)
    if (type(a) == type({})) and (type(b) == type({})) then
        return 1
    elseif (type(a) == type({})) and (type(b) == type(1)) then
        return 2
    elseif (type(a) == type(1)) and (type(b) == type({})) then
        return 3
    else
        error('One or more of the elements are not a table/array')
    end
end


function numpy.array (values)
    local array = {}
    setmetatable(array, mt)
    for _, v in ipairs(values) do
        array[_] = v 
    end
    
    return array
end

function numpy.add (a,b)
    local res = numpy.array{}
    case = cases(a,b)
    
    if (case == 1)  and (len(a) == len(b)) then
        for k in pairs(a) do
            res[k] = a[k] + b[k]
        end
    
    elseif case == 2 then
        for k in pairs(a) do
            res[k] = a[k] + b
        end
    
    elseif case == 3 then
        for k in pairs(b) do
            res[k] = a + b[k]
        end
    end
    return res
end

function numpy.subtract (a,b)
    local res = numpy.array{}
    case = cases(a,b)
    
    if (case == 1)  and (len(a) == len(b)) then
        for k in pairs(a) do
            res[k] = a[k] - b[k]
        end
    
    elseif case == 2 then
        for k in pairs(a) do
            res[k] = a[k] - b
        end
    
    elseif case == 3 then
        for k in pairs(b) do
            res[k] = a - b[k]
        end
    end
    return res
end

function numpy.multiply (a,b)
    local res = numpy.array{}
    case = cases(a,b)
    
    if (case == 1)  and (len(a) == len(b)) then
        for k in pairs(a) do
            res[k] = a[k] * b[k]
        end
    
    elseif case == 2 then
        for k in pairs(a) do
            res[k] = a[k] * b
        end
    
    elseif case == 3 then
        for k in pairs(b) do
            res[k] = a * b[k]
        end
    end
    return res
end

function numpy.divide (a,b)
    local res = numpy.array{}
    case = cases(a,b)
    
    if (case == 1)  and (len(a) == len(b)) then
        for k in pairs(a) do
            res[k] = a[k] / b[k]
        end
    
    elseif case == 2 then
        for k in pairs(a) do
            res[k] = a[k] / b
        end
    
    elseif case == 3 then
        for k in pairs(b) do
            res[k] = a / b[k]
        end
    end
    return res
end

mt.__add = numpy.add
mt.__sub = numpy.subtract
mt.__mul = numpy.multiply
mt.__div = numpy.divide

"""

dict_funcs['string_join'] = """
function join(tbl)
    return table.concat(tbl, string.char(10))
end

"""

# dict_funcs['out_type'] = """
# 
# 
# 
# """

def grab_func(name):
    return dict_funcs[name]
