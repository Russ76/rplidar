#!/usr/bin/env python3
'''Records measurments to a given file. Usage example:

$ ./record_measurments.py out.txt'''
import sys
import time
import asyncio
from rplidar import RPLidar
import PyCmdMessenger
import math

angleoffset = 45
gain = 2
speed = 70
left = 0
right = 0

PORT_NAME = '/dev/ttyUSB0' # this is for the Lidar

# Initialize an ArduinoBoard instance.  This is where you specify baud rate and
# serial timeout.  If you are using a non ATmega328 board, you might also need
# to set the data sizes (bytes for integers, longs, floats, and doubles).  
myarduino = PyCmdMessenger.ArduinoBoard("/dev/ttyACM0",baud_rate=9600)

# List of commands and their associated argument formats. These must be in the
# same order as in the sketch.
commands = [["motors","iii"], # motor power, left, right
            ["get_sonar",""], # commands a sonar sample
            ["sonar","i"], # result of sonar sample
            ["sonar_angle","i"], # commands a sonar servo angle
            ["line_tracker","iiii"], # output of line-follower senors
            ["ir_in","f"], # commands from IR remote control
            ["error","s"]]

# Initialize the messenger
c = PyCmdMessenger.CmdMessenger(myarduino,commands)

def tic():
    return 'at %1.1f seconds' % (time.time() - start)

async def gr1():
    # Busy waits for a tenth of a second, but we don't want to stick around...
    print('10Hz loop started work: {}'.format(tic()))
    time1 = time.time()
    while True:
      # do some work here
      await asyncio.sleep(0)
      if time.time() > time1 + 0.1:
        print('10Hz loop ended work: {}'.format(tic()))
        time1 = time.time()

async def gr2():
    # Busy waits for a second, but we don't want to stick around...
    print('1 Hz loop started work: {}'.format(tic()))
    time2 = time.time()
    while True:
      # do some work here
      await asyncio.sleep(0)
      if time.time() > time2 + 1:
        print('1 Hz loop ended work: {}'.format(tic()))
        time2 = time.time()

async def gr3():
    print("Let's do some stuff while the coroutines are blocked, {}".format(tic()))
    time3 = time.time()
    while True:
      # do some work here
      if time.time() > time3 + 20:
        print("Done!")
      await asyncio.sleep(0)

def drive(angle):
    global speed
    global gain
    # Send motor commands
    steer = int(100*math.atan(math.radians(angle)))
    print ("steer: ", steer * gain)
    if steer <= 0:
        right = -1 * steer * gain
        left = 0
    else:
        left = steer * gain
        right = 0
    print (speed, left, right) 
    c.send("motors",speed,left,right)

def scan(lidar):
    try:
        counter = 0
        print('Recording measurements... Press Crl+C to stop.')
        data = 0
        lasttime = time.time()
        for measurment in lidar.iter_measurments():
            if (measurment[2] > 0 and measurment[2] < 90):  # in angular range
                if (measurment[3] < 1000 and measurment[3] > 100): # in distance range
                    data = data + measurment[2] # angle
                    counter = counter + 1 # increment counter
            if time.time() > (lasttime + 0.1):
                print("this should happen ten times a second")
                if counter > 0:  # this means we see something
                    average_angle = data/counter
                    print ("Average Angle: ", average_angle-angleoffset)
#                    drive (average_angle-angleoffset)
                lasttime = time.time()  # reset 10Hz timer
    except KeyboardInterrupt:
        print('Stopping.')
        lidar.stop()
        lidar.stop_motor()
        c.send("motors",0,0,0)  # turn off wheel motors
        lidar.disconnect()

def run():
    '''Main function'''
    drive (0) # start
    lidar = RPLidar(PORT_NAME)
    lidar.start_motor()
    time.sleep(1)
    info = lidar.get_info()
    print(info)
#    ioloop = asyncio.get_event_loop()
#    tasks = [
#    	    ioloop.create_task(gr1()),
#    	    ioloop.create_task(gr2()),
#    	    ioloop.create_task(gr3())
#	    ]
#    ioloop.run_until_complete(asyncio.wait(tasks))
#    ioloop.close()
    while True:
        scan(lidar)
 
if __name__ == '__main__':
    run()
