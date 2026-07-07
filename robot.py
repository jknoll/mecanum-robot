from adafruit_motorkit import MotorKit
kit = MotorKit()
from time import sleep
from pprint import pprint as pp

backward = [1, 1, 1, 1]
forward = [-1, -1, -1, -1]
clockwise  = [1, 1, -1, -1]
counterclockwise = [-1, -1, 1, 1]
right = [-1, 1, -1, 1]
left = [1, -1, 1, -1]
ten = [1, 0, 1, 0]
two = [0, 1, 0, 1]
four = [-1, 0, -1, 0]
eight = [0, -1, 0, -1]
stop = [0, 0, 0, 0]
roundclockwise = [0, 0, 1, 1]
spinclockwise = [-1, 0, 0, 1]

def drive(command, kit):
  pp(command)
  kit.motor1.throttle = command[0]
  kit.motor2.throttle = command[1]
  kit.motor3.throttle = command[2]
  kit.motor4.throttle = command[3]

'''
import keyboard  # using module keyboard
while True:  # making a loop
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('w'):  # if key 'w' is pressed 
            drive(forward, kit)
            print('w')
        if keyboard.is_pressed('a'):  # if key 'w' is pressed 
            drive(left, kit)
        if keyboard.is_pressed('s'):  # if key 'w' is pressed 
            drive(back, kit)
        if keyboard.is_pressed('d'):  # if key 'w' is pressed 
            drive(right, kit)
        if keyboard.is_pressed(','):  # if key 'w' is pressed 
            drive(counterclockwise, kit)
        if keyboard.is_pressed('.'):  # if key 'w' is pressed 
            drive(clockwise, kit)
        if keyboard.is_pressed(' '):  # if key 'w' is pressed 
            drive(stop, kit)
    except Exception as e:
        print(e.message, e.args)	
        break
'''
'''
duration = 1
drive(forward, kit)
sleep(duration)
drive(backward, kit)
sleep(duration)
drive(clockwise, kit)
sleep(duration)
drive(counterclockwise, kit)
sleep(duration)
drive(right, kit)
sleep(duration)
drive(left, kit)
sleep(duration)
drive(two, kit)
sleep(duration)
drive(four, kit)
sleep(duration)
drive(roundclockwise, kit)
sleep(duration)
drive(spinclockwise, kit)
sleep(duration)
drive(stop, kit)
'''
