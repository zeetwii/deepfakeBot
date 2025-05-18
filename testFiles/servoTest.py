import time # needed for sleep
import datetime # needed for timestamps
import random # needed for random number generation
from adafruit_servokit import ServoKit # needed for servo movements
# setup servo kit
kit = ServoKit(channels=16)
kit.servo[0].actuation_range = 270
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)
print("init servos")
kit.servo[0].angle = 90
kit.servo[1].angle = 90
time.sleep(1)
print("Initalization finished")

oldYawAngle = 90
oldPitchAngle = 90

def slowMovePitchYaw(yawAngle, pitchAngle):
    """
    Slowly moves the servos to the desired angles
    """
    global oldYawAngle
    global oldPitchAngle

    # calculate the difference between the current and desired angles
    yawDiff = yawAngle - oldYawAngle
    pitchDiff = pitchAngle - oldPitchAngle

    # move the servos in small increments
    for i in range(0, 100, 5):
        kit.servo[0].angle = oldYawAngle + (yawDiff * i / 100)
        kit.servo[1].angle = oldPitchAngle + (pitchDiff * i / 100)
        time.sleep(0.025)

    # update the old angles
    oldYawAngle = yawAngle
    oldPitchAngle = pitchAngle


while True:
	#yawAngle = random.randint(5, 175)
	#pitchAngle = random.randint(5, 175)
	
    inputString = input("Enter angles (yaw pitch) or 'q' to quit: ")
    if inputString == 'q':
        break
    try:
        yawAngle, pitchAngle = map(int, inputString.split(" "))

        #print(f"Setting angles to {str(yawAngle)} and {str(pitchAngle)}")
        slowMovePitchYaw(yawAngle, pitchAngle)
        #kit.servo[0].angle = yawAngle
        #kit.servo[1].angle = pitchAngle

    except ValueError:  # handle invalid input      
        print("Invalid input. Please enter two integers separated by a comma.")
        continue
    

    
	#time.sleep(5) # give time for everything to move and stabalize
	
