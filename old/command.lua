
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


function join(tbl)
    return table.concat(tbl, string.char(10))
end

data = io.open("/Users/danny/casa/fitsidi/data.txt","r")
py_obj = data:read("*all")
data:close()
py_obj = py_obj:gsub("%[","")
py_obj = py_obj:gsub("%]","")
py_obj = split(py_obj,",")

  function interleave(a)
    z = table.maxn(a)/2
    c= {}
    for i=1,z do table.insert(c,a[i]) table.insert(c,a[x+i]) end  
    return c
  end
  
  po = py_obj
  
  --b = py_obj[2]
  --print(a)
  --c = a
  lo = po
  
out_type = io.open("/Users/danny/casa/fitsidi/out_type.txt","w")
out_type:write(type(lo))
out_type:close()

function output(var)
if (type(var) == type("str")) or (type(var) == type(1)) then
new_data = io.open("/Users/danny/casa/fitsidi/new_data.txt","w")
new_data:write(lo)
new_data:close()
end
if (type(var) == type({1,2})) then
lo= join(lo)
new_data = io.open("/Users/danny/casa/fitsidi/new_data.txt","w")
new_data:write(lo)
new_data:close()

end 
end
output(lo)