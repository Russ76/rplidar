#!/usr/bin/env python3
'''Records measurments to a given file. Usage example:

$ ./record_measurments.py out.txt'''
import sys
import time
from rplidar import RPLidar
import math
import Adafruit_PCA9685


# Initialise the PCA9685 servo driver board using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

angle_offset = 50 # this compensates for the Lidar being placed in a rotated position
gain = 2 # this is the steering gain. The PWM output to the steering servo must be between 0 (left) and 200 (right)
speed = 1000 # crusing speed, must be between 0 and 3600
steering_correction = -10 # this compensates for any steering bias the car has. Positive numbers steer to the right
start = time.time()
stop = False
left_motor = 4
right_motor = 5

PORT_NAME = '/dev/ttyUSB0' # this is for the Lidar

def drive(speed):  # speed must be between 0 and 3600
    servo (left_motor,speed)
    servo (right_motor,speed)

def servo (channel, PWM):
    pulse = PWM + 300 # make sure pulse width at least 500
    pwm.set_pwm(channel,0, pulse) # channel, start of wave, end of wave

def steer(angle):
    global gain
    drive (speed)
    angle = int(100 + gain*angle)
    print (angle)
    servo (0,angle)
    # Send motor commands

def scan(lidar):
    global stop
    time1 = time.time()
    while True:
        counter = 0
        print('Recording measurements... Press Crl+C to stop.')
        data = 0
        range_sum = 0
        lasttime = time.time()
        for measurment in lidar.iter_measurments():
            if stop == True:
                lidar.stop()
                lidar.stop_motor()
                drive(0)
                lidar.disconnect()
                break
            if (measurment[2] > 0 and measurment[2] < 90):  # in angular range
                if (measurment[3] < 1000 and measurment[3] > 100): # in distance range
                    data = data + measurment[2] # angle weighted by distance; basically we're coming up with an obstacle centroid
#                    range_sum = range_sum + measurment[3] # sum all the distances so we can normalize later
                    counter = counter + 1 # increment counter
            if time.time() > (lasttime + 0.1):
#                print("this should happen ten times a second")
                if counter > 0:  # this means we see something
                    average_angle = (data/counter) - angle_offset # average of detected angles
                    obstacle_direction = int(100*math.atan(math.radians(average_angle)))  # convert to a vector component
                    drive_direction = -1 * obstacle_direction # steer in the opposite direction as obstacle (I'll replace this with a PID)
                    print ("Drive direction: ", drive_direction)
                    counter = 0 # reset counter
                    data = 0  # reset data
                    range_sum = 0
                else:
                    drive_direction = 0
                steer(drive_direction)  # Send data to motors
                lasttime = time.time()  # reset 10Hz timer

def run():
    '''Main function'''
    lidar = RPLidar(PORT_NAME)
    lidar.start_motor()
    time.sleep(1)
    info = lidar.get_info()
    print(info)
    try:
        scan(lidar)
    except KeyboardInterrupt:
        stop = True
        print('Stopping.')
        lidar.stop()
        lidar.stop_motor()
        drive (0)
        lidar.disconnect()
 
if __name__ == '__main__':
    run()
