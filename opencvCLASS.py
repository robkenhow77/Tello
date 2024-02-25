import cv2 as cv
from djitellopy import Tello
import numpy as np


# Camera Matrix and Distortion Coefficients. This is the data from tello
class OpenCV:

    CameraMatrix = np.array([[902.56969157,   0.,         480.06685807],
                             [  0.,         912.82526291, 362.35651128],
                             [  0.,           0.,           1.        ]])

    DistortionCoefficients = np.array([-1.62122392e-02, -5.72842162e-02,  1.26644062e-03,  1.31155587e-04,
                                       1.89141453e-01])

    marker_size_a_cm = 14.5     # Replace with your actual marker size.
    marker_size_b_cm = 1.6      # Replace with your actual marker size.
    # The large aruco is 14.5cm x 14.5cm (5.7 inches x 5.7 inches)
    # The small aruco is 1.6cm x 1.6cm (0.63 inches x 0.63 inches)


    def obj_points(self, marker_length):
        return np.array(
    [[-marker_length / 2, -marker_length / 2, 0],
              [marker_length / 2, -marker_length / 2, 0],
              [marker_length / 2, marker_length / 2, 0],
              [-marker_length / 2, marker_length / 2, 0]], dtype=np.float32)


            # np.array([
            # [0, 0, 0],               # Top-left corner
            # [marker_length, 0, 0],    # Top-right corner
            # [marker_length, marker_length, 0],  # Bottom-right corner
            # [0, marker_length, 0]     # Bottom-left corne
            # ], dtype=np.float32)



    DICT = {
        "ArucoA": cv.aruco.DICT_7X7_250,
        "ArucoB": cv.aruco.DICT_6X6_250}
    parameters = cv.aruco.DetectorParameters()

    # Aruco A = 7x7
    arucoDictA = cv.aruco.getPredefinedDictionary(DICT["ArucoA"])
    aruco_detectorA = cv.aruco.ArucoDetector(arucoDictA, parameters)
    # Aruco B = 6x6
    arucoDictB = cv.aruco.getPredefinedDictionary(DICT["ArucoB"])
    aruco_detectorB = cv.aruco.ArucoDetector(arucoDictB, parameters)

    # SubPix
    zeroZone = (-1,-1)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    winSize = (5, 5)

    def pose(self, frame):
        # frame = frame_read.frame
        # Flip image due to mirror
        frame = cv.flip(frame, 0)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Search for corners
        corners_a, ids_a, rejected_img_points_a = cv.aruco.ArucoDetector.detectMarkers(OpenCV.aruco_detectorA, gray)
        corners_b, ids_b, rejected_img_points_b = cv.aruco.ArucoDetector.detectMarkers(OpenCV.aruco_detectorB, gray)

        #                               PERFORM CALCULATIONS IF THE ARUCOS CAN BE DETECTED

        if corners_a != ():  # If the large aruco can be seen, perform some distance calculations
            corners_a2 = cv.cornerSubPix(gray, corners_a[0], OpenCV.winSize, OpenCV.zeroZone, OpenCV.criteria)
            corners_a2 = tuple(np.array([corners_a2]))
            # Find the rotation and translation vectors.
            ret_a, rvecs_a, tvecs_a = cv.solvePnP(OpenCV.obj_points(self, OpenCV.marker_size_a_cm), corners_a2[0], OpenCV.CameraMatrix, OpenCV.DistortionCoefficients)
            Ra, _ = cv.Rodrigues(rvecs_a)
            xRa = cv.RQDecomp3x3(Ra)
            xa, ya, za, pitch_a, roll_a, yaw_a = tvecs_a[0], tvecs_a[1], tvecs_a[2], xRa[0][0], xRa[0][1], xRa[0][2]

        if corners_b != ():  # If the small aruco can be seen, perform some distance calculations
            corners_b2 = cv.cornerSubPix(gray, corners_b[0], OpenCV.winSize, OpenCV.zeroZone, OpenCV.criteria)
            corners_b2 = tuple(np.array([corners_b2]))
            # Find the rotation and translation vectors.
            ret_b, rvecs_b, tvecs_b = cv.solvePnP(OpenCV.obj_points(self, OpenCV.marker_size_b_cm), corners_b2[0], OpenCV.CameraMatrix, OpenCV.DistortionCoefficients)
            Rb, _ = cv.Rodrigues(rvecs_b)
            xRb = cv.RQDecomp3x3(Rb)
            xb, yb, zb, pitch_b, roll_b, yaw_b = tvecs_b[0], tvecs_b[1], tvecs_b[2], xRb[0][0], xRb[0][1], xRb[0][2]

        #                               POTENTIAL RETURN VALUES BASED ON WHICH ARUCOS ARE DETECTED
        #       return (x,y,z from aruco a), (x,y,z from aruco b), (angles from aruco a), (angles from aruco b)
        # r[3] = roll
        #

        if corners_a != () and corners_b != ():   # If the large aruco and the small aruco can be seen, return this
            gray2 = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
            # Add the id and corner
            gray3_ = cv.aruco.drawDetectedMarkers(gray2, corners_a2, ids_a)
            gray3 = cv.aruco.drawDetectedMarkers(gray3_, corners_b2, ids_b)
            # Draws the axis
            img_ = cv.drawFrameAxes(gray3, OpenCV.CameraMatrix, OpenCV.DistortionCoefficients, rvecs_a, tvecs_a, 2)
            img = cv.drawFrameAxes(img_, OpenCV.CameraMatrix, OpenCV.DistortionCoefficients, rvecs_b, tvecs_b, 0.7)
            # print("Both arucos detected")
            return xa, ya, za, xb, yb, zb, pitch_a, roll_a, yaw_a, pitch_b, roll_b, yaw_b, img

        if corners_a != () and corners_b == ():   # If only the large aruco can be seen return this
            gray2 = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
            # Add the id and corner
            gray3 = cv.aruco.drawDetectedMarkers(gray2, corners_a2, ids_a)
            # Draws the axis
            img = cv.drawFrameAxes(gray3, OpenCV.CameraMatrix, OpenCV.DistortionCoefficients, rvecs_a, tvecs_a, 2)
            # print("Large aruco detected")
            return xa, ya, za, -1, -1, -1, pitch_a, roll_a, yaw_a, -1, -1, -1, img

        if corners_a == () and corners_b != ():  # If only the small aruco can be seen return this
            gray2 = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
            # Add the id and corner
            gray3 = cv.aruco.drawDetectedMarkers(gray2, corners_b2, ids_b)
            # Draws the axis
            img = cv.drawFrameAxes(gray3, OpenCV.CameraMatrix, OpenCV.DistortionCoefficients, rvecs_b, tvecs_b, 0.7)
            # print("Small aruco detected")
            return -1, -1, -1, xb, yb, zb, -1, -1, -1, pitch_b, roll_b, yaw_b, img

        else:   # If neither can be seen return this
            # print("No arucos detected")
            return -1, -1, -1, -1, -1, -1,-1, -1, -1, -1, -1, -1, gray
    
# OLD
# if corners_a != ():
#     corners_a2 = cv.cornerSubPix(gray, corners_a[0], OpenCV.winSize, OpenCV.zeroZone, OpenCV.criteria)
#     corners_a2 = tuple(np.array([corners_a2]))
#     # Find the rotation and translation vectors.
#     ret, rvecs, tvecs = cv.solvePnP(OpenCV.object_points, corners_a2[0], OpenCV.CameraMatrix,
#           OpenCV.DistortionCoefficients)
#
#     distance_x = tvecs[0]
#     distance_y = tvecs[1]
#     distance_z = tvecs[2]
#
#     print("X Distance:", distance_x)
#     print("Y Distance:", distance_y)
#     print("Z Distance:", distance_z)
#
#     gray2 = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
#     # Add the id and corner
#     # print(corners_a)
#     g3 = cv.aruco.drawDetectedMarkers(gray2, corners_a2, ids_a)
#     # Draws the axis
#     img = cv.drawFrameAxes(g3, OpenCV.CameraMatrix, OpenCV.DistortionCoefficients, rvecs, tvecs, 0.5)

# Need to return xa, ya, za, xb, yb, zb, img



    def extract(self,word):
        s = 0
        c = 0
        angles = []
        for i in range(len(word)):
            # print(word[i])
            if word[i] == ':':
                c = i
                # print("c = ", c)
            if word[i] == ';':
                s = i
                # print("s = ", s)
            try:
                if s > 1 and c > 1:
                    angles.append(int(word[c + 1:s]))
                    c, s = 0, 0
            except:
                None

        return angles

