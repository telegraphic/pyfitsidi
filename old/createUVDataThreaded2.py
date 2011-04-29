import time
import threading
import Queue    
import StringIO       

import sys, os
import pyfits as pf, numpy as np, tables as tb

my_queue = Queue.Queue()
time_of_last_run = time.time()

class queue_runner(threading.Thread):
  """Threaded Queue runner for testing things"""
  def __init__(self, my_queue):      
      threading.Thread.__init__(self)           
      self.my_queue = my_queue                
                                                
  def run(self):                                
    global time_of_last_run                     

    while True:
      try:     
        my_id = self.my_queue.get(True, 2)
      except:                               
        if time.time() - time_of_last_run > 3:
          return                              
      else:                                   
        if my_id:                            
          time_of_last_run = time.time()
          
          time.sleep(1)
          self.my_queue.task_done()

def main():
  global time_of_last_run
  time_of_last_run = time.time()
  
  if True:
    #spawn a pool of place worker threads
    for i in range(50):
      p = queue_runner(my_queue)
      p.setDaemon(True)
      p.start()

    #now load some arbitrary jobs into the queue
    for i in range(5000):
       my_queue.put(i)

    print "Running..."
    while time.time() - time_of_last_run < 3:
      print ">> qsize %s threadCount %s" % (my_queue.qsize(),threading.activeCount())
      time.sleep(2)

    time.sleep(4)
    my_queue.join()

if __name__ == "__main__":
  main()
