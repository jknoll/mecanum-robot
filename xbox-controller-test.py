from evdev import InputDevice, categorize, ecodes, list_devices
from adafruit_motorkit import MotorKit

import time

# Initialize motor controller
kit = MotorKit()
speed = 1.0  # Moderate throttle value

# Motor mapping: adjust as needed for your wiring
# N.B. this isn't in sync with the wiring, but forward/backward and strafe left/right are working. m4 is fl, m3 is bl.
# TODO: fix this.
# 
# motor1 = front-left
# motor2 = front-right
# motor3 = back-left
# motor4 = back-right

motors = [kit.motor1, kit.motor2, kit.motor3, kit.motor4]

def find_controller(name="Xbox Wireless Controller"):
    for path in list_devices():
        device = InputDevice(path)
        if name in device.name:
            return device
    raise RuntimeError(f"Controller '{name}' not found.")

def stop():
    for m in motors:
        m.throttle = 0
    print("stop()")

def move(forward=0, strafe=0):
    """
    Simple mecanum logic for D-pad only (no rotation).
    `forward`: +1 = forward, -1 = backward
    `strafe`: +1 = right, -1 = left
    """

    # Strafe also needs to be inverted (+ and - switched), perhaps also due to motor order being different.
    fl = -1 * forward + strafe
    fr = forward + strafe
    bl = -1 * forward + strafe # Left hand motors need to have forward inverted to match right hand motors; they are actually fl and bl, but see comment above in motors=[]
    br = -1 * forward - strafe

    # Normalize so no value exceeds abs(1.0)
    max_val = max(abs(fl), abs(fr), abs(bl), abs(br), 1)
    fl, fr, bl, br = [speed * v / max_val for v in (fl, fr, bl, br)]

    kit.motor1.throttle = fl   # front-left
    kit.motor2.throttle = fr   # front-right
    kit.motor3.throttle = bl   # back-left
    kit.motor4.throttle = br   # back-right

    print("move")
    print(fl, fr, bl, br)


def move_rotate(rotate):
    if rotate == 'l':
      kit.motor1.throttle = -speed   # front-left
      kit.motor2.throttle = speed   # front-right
      kit.motor3.throttle = speed   # back-left
      kit.motor4.throttle = speed   # back-right
    elif rotate == 'r':
      kit.motor1.throttle = speed   # front-left
      kit.motor2.throttle = -speed   # front-right
      kit.motor3.throttle = -speed   # back-left
      kit.motor4.throttle = -speed   # back-right
    print("move_rotate")

def main():
    dev = find_controller()
    print(f"Connected to: {dev.name} ({dev.path})")

    for event in dev.read_loop():
        rotate_value = 0
        x, y = 0, 0  # D-pad state

        if event.type == ecodes.EV_ABS:
            absevent = categorize(event)
            print(categorize(event))
            if absevent.event.code == ecodes.ABS_HAT0X:
                x = absevent.event.value
            elif absevent.event.code == ecodes.ABS_HAT0Y:
                y = absevent.event.value
            elif absevent.event.code == ecodes.ABS_RZ:
                rotate = 'r'
                rotate_value = absevent.event.value
                print(rotate_value)
            elif absevent.event.code == ecodes.ABS_Z:
                rotate = 'l'
                rotate_value = absevent.event.value

            if (x, y) == (0, 0) and rotate_value < 20:
                stop()
            
            if (x, y) != (0, 0):
                move(forward=y, strafe=x)  # Y is inverted
            
            if (rotate_value != 0):
                move_rotate(rotate)
                
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop()
