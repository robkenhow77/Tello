from djitellopy import Tello
import numpy as np
import cv2 as cv
import pygame
from opencvCLASS import OpenCV
from Transform import Transform
import time
import math
from Averaging import Average


av = Average()
transform = Transform()
ocv = OpenCV()


# Initialise
tello = Tello()
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()

# Pygame
pygame.init()
display = pygame.display.set_mode((300, 300))


# Functions
def command(message):
    for i in range(3):
        tello.send_command_without_return(message)


def commandResponse(message):
    for i in range(3):
        tello.send_command_with_return(message)


def end():
    tello.streamoff()
    tello.end()


# Move function, allows small movements
# Insert the values for movement. USE 25 FOR XY AND -40 FOR Z
# t1 is the time that the drone moves at a given speed
def move(mx, my, mz, t1=0.15, t2=0.1):
    print("rx: ", rx)
    print("ry: ", ry)
    print("rz: ", rz)
    command('rc ' + str(mx) + ' ' + str(my) + ' ' + str(mz) + ' 0')
    time.sleep(t1)
    command('rc 0 0 0 0')
    time.sleep(t2)
    # Working for speed=20, sleep1=0.15, sleep2 = 0.05
    return


# Initialisation - pre-takeoff
takeoff = False
while True:
    if takeoff:
        break
    # Display camera feed
    frame = frame_read.frame
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cv.imshow('Preview', gray)

    # Pygame buttons
    for event in pygame.event.get():
        # checking if keydown event happened or not
        if event.type == pygame.KEYDOWN:

            "Get battery (b)"
            if event.key == pygame.K_b:
                commandResponse('battery?')

            "Takeoff (t)"
            if event.key == pygame.K_t:
                takeoff = True
                print("TAKEOFF")

            "Abort (k)"
            if event.key == pygame.K_k:
                end()
                exit()


# Main loop
# Speed and distance
# rx, ry, rz = 0, 0, 0    # Initial speeds, rc is the remote control speed rc' 0 0 0 0 '
zone1 = 7     # Over the target, hover if within, if greater go zone1_speed
zone2 = 75
zone2speed = 25
# Average positioning
x_array = []
y_array = []
z_array = []
# Sets the initial array
for i in range(20):
    x_array.append(0)
    y_array.append(0)
    z_array.append(100)

average_position_arrays = [x_array, y_array, z_array]
means = [0, 0, 0]   # x,y,z
# Other
stop = False
manual = True
lost_count = 0
aruco_count = 0
tello.takeoff()
while True:
    # CAMERA
    frame = frame_read.frame
    xa, ya, za, xb, yb, zb, pitch_a, roll_a, yaw_a, pitch_b, roll_b, yaw_b, img = ocv.pose(frame)
    # 1 denotes the large aruco, 2 denotes the small aruco
    x1, y1, z1 = transform.transfunc(pitch_a, roll_a, yaw_a, xa, ya, za)
    x2, y2, z2 = transform.transfunc(pitch_b, roll_b, yaw_b, xb, yb, zb)
    cv.imshow('Preview', img)

    # Manual Mode
    if manual:
        # Pygame buttons - manual controls
        for event in pygame.event.get():
            # checking if keydown event happened or not
            if event.type == pygame.KEYDOWN:

                # FORWARDS
                if event.key == pygame.K_w:
                    command('rc 0 30 0 0')
                    print("FORWARD")

                # BACKWARDS
                if event.key == pygame.K_s:
                    command('rc 0 -30 0 0')
                    print("BACKWARD")

                # LEFT
                if event.key == pygame.K_a:
                    command('rc -30 0 0 0')
                    print("LEFT")

                # RIGHT
                if event.key == pygame.K_d:
                    command('rc 30 0 0 0')
                    print("RIGHT")

                # UP
                if event.key == pygame.K_e:
                    command('rc 0 0 30 0')
                    print("UP")

                # DOWN
                if event.key == pygame.K_q:
                    command('rc 0 0 -30 0')
                    print("DOWN")

                # HOVER
                if event.key == pygame.K_h:
                    command('rc 0 0 0 0')
                    print("HOVER")

                # LAND
                if event.key == pygame.K_k:
                    command('rc 0 0 0 0')
                    stop = True
                    print("LAND")

                # AUTOPILOT
                if event.key == pygame.K_1:
                    command('rc 0 0 0 0')
                    manual = False
                    print("AUTOPILOT")

    # Autopilot
    if not manual:

        # ##### AUTOPILOT SCRIPT ####
        # If the aruco can't be seen, does approximately 33 frames per second.
        # If the aruco is lost then move upwards. WILL BE UPDATED TO SEARCH MODE.
        if lost_count >= 120:
            command('rc 0 0 20 0')
            print("aruco lost ")

        if x1 == 1 and x2 == 1:
            lost_count += 1

        else:
            # If the large aruco can be seen, use it, else use the small aruco
            if x1 != 1:
                x, y, z = x1, y1, z1
                yaw = yaw_a
            # If the large aruco can be seen
            else:
                x, y, z = x2, y2, z2
                yaw = yaw_b

            # Counters
            lost_count = 0
            aruco_count += 1    # +1 frame of seeing the aruco

            # Average positioning
            position = [x, y, z]
            for i in range(3):
                average_position_arrays[i].append(position[i][0])
                average_position_arrays[i].pop(0)

            # Movement. Only allow movement if the aruco has been seen for 10 frames/iterations.
            # # TRY CHANGING THIS BUT REMEMBER TO CHANGE THE ARRAY LENGTH OF THE AVERAGE POSITIONS
            if aruco_count >= 20:
                for i in range(3):
                    # print(average_position_arrays[i])
                    # print(av.cut(average_position_arrays[i], 4))
                    means[i] = np.mean(av.cut(average_position_arrays[i], 5))
                x, y, z = means[0], means[1], means[2]
                y = y + 7  # ERROR ADJUSTMENT
                radius = (x ** 2 + y ** 2) ** 0.5
                # print("radius", radius)
                # Yaw Correction, allow a +-10º
                if yaw > 10:
                    tello.rotate_clockwise(int(abs(yaw)))
                elif yaw < -10:
                    tello.rotate_counter_clockwise(int(abs(yaw)))
                print("x : ", x)
                print("y : ", y)
                print("z : ", z)
                # print("x array: ", x_array)
                # print("y array: ", y_array)
                # print("z array: ", z_array)
                #  Radial distance
                if radius < zone1:
                    print("zone 1")
                    rx = 0
                    ry = 0
                    rz = -40
                    if z < 35 and radius < zone1 - 2:  # If the drone is
                        print("Landing")
                        stop = True
                        break
                    elif z < 60:
                        move(rx, ry, rz)
                    else:
                        move(rx, ry, rz, t1=1.5)    # was 0.5

                elif radius < zone2:
                    print("zone 2")
                    # if x > zone1:
                    #     rx = 20
                    # elif x < -zone1:
                    #     rx = -20
                    # else:
                    #     rx = 0
                    #
                    # if y > zone1:
                    #     ry = 20
                    # elif y < -zone1:
                    #     ry = -20
                    # else:
                    #     ry = 0

                    # Does similar to above in a more mathematical approach
                    # Could make the speed a function of height 
                    theta = math.atan(abs(y)/abs(x))
                    rx = zone2speed * math.cos(theta)
                    ry = zone2speed * math.sin(theta)
                    rx = rx * x/abs(x)
                    ry = ry * y/abs(y)
                    rx = round(rx, 0)
                    ry = round(ry, 0)
                    if radius <= z * math.tan(math.radians(10)):
                        rz = -40
                    else:
                        rz = 0

                    # if z < 60:
                    #     move(rx, ry, rz, t1=0.3)
                    # else:
                    #     move(rx, ry, rz, t1=0.5)
                    t = 0.2 + radius/60
                    if t > 0.8:
                        t = 0.8
                    print("t: ", t)
                    move(rx, ry, rz, t1=t)
                else:
                    print("zone 3")
                    if x > 30:
                        rx = 30
                    elif x < -30:
                        rx = -30
                    else:
                        rx = 0

                    if y > 30:
                        ry = 30
                    elif y < -30:
                        ry = -30
                    else:
                        ry = 0

                    command('rc ' + str(rx) + ' ' + str(ry) + ' 0 0')

                aruco_count = 0

        # #### END OF AUTOPILOT SCRIPT ####

        # Pygame buttons - autopilot controls
        for event in pygame.event.get():
            # checking if keydown event happened or not
            if event.type == pygame.KEYDOWN:
                # MANUAL AND EMERGENCY LAND
                # SWITCHES FROM AUTOPILOT TO MANUAL
                if event.key == pygame.K_m:
                    command('rc 0 0 0 0')
                    manual = True
                    print("MANUAL")

                # END LOOP
                if event.key == pygame.K_k:
                    command('rc 0 0 0 0')
                    stop = True

    # Prints
    # print("x :", means[0])
    # print("y :", means[1])
    # print("z :", means[2])
    # ENDS THE LOOP
    if stop:
        break

# End sequence
tello.land()
end()

# Notes
# Need a search mode
# Create a pop-up or picture of controls


# Try not setting speed each loop only at certain points!!!!!
# Use an algorithm and zones to determine if the command needs to change.
# For example if it's moving towards the marker and hasn't got it then it doesn't need a new move command,
# unless it's close and needs to slow down
# Use a variable that describes what it's doing.
# start with if it's +-10cm, hover, 10-30 move at 15 speed, >30 move at 30 speed
# Currently too much overshoot

# Start switching between the main aruco and the embedded,
# Decide a point when you should switch then use an if and make the x, y z values from the embedded
# Create a flow diagram and skeleton code

# need one section for adding to the array then another to cut it
