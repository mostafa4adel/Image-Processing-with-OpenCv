"""
    Author: Mostafa Adel
    Date: 10/3/2021
    version: 1.1
    Title: OpenCv Task
    Description: I have solved the problems :
                * I increased the frame rate of video recording.
                * I enabled the user to switch between color and gray when the video is paused.
                * I added a reset button.
                * I removed the unnecessary try and except.
"""

import cv2
import os
import math

frame = None
rectanglesPoints = []
circlePoints = []
linePoints = []

drawingMode = None
pointsEntered = 0
userWantToDraw = False
roi_points = []
roi_wanted = False
scale_percent = 100


def click_event(event, x, y, flags, param):
    global userWantToDraw, pointsEntered, drawingMode
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"({x}, {y})")
        if userWantToDraw:
            if drawingMode == 't':
                pointsEntered += 1
                rectanglesPoints.append(tuple([x, y]))

            if drawingMode == 'l':
                pointsEntered += 1
                linePoints.append(tuple([x, y]))

            if drawingMode == 'c':
                pointsEntered += 1
                circlePoints.append(tuple([x, y]))

            if drawingMode == 'i':
                pointsEntered += 1
                roi_points.append(tuple([x, y]))

    if pointsEntered == 2:
        userWantToDraw = False
        pointsEntered = 0


def scaled(src):
    width = int(src.shape[1] * scale_percent / 100)
    height = int(src.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(src, dim, interpolation=cv2.INTER_AREA)
    return dim, resized


def update_frame():
    global frame, rectanglesPoints, circlePoints, linePoints, points

    if len(rectanglesPoints) != 0:
        for i in range(0, len(rectanglesPoints), 2):
            if (i + 1) < len(rectanglesPoints):
                cv2.rectangle(frame, rectanglesPoints[i], rectanglesPoints[i + 1], (0, 255, 0), 1)

    if len(circlePoints) != 0:
        for i in range(0, len(circlePoints), 2):
            if (i + 1) < len(circlePoints):
                cv2.circle(frame, circlePoints[i], int(math.sqrt(
                    ((circlePoints[i][0] - circlePoints[i + 1][0]) ** 2) + (
                            (circlePoints[i][1] - circlePoints[i + 1][1]) ** 2))), (0, 0, 255), 1)

    if len(linePoints) != 0:
        for i in range(0, len(linePoints), 2):
            if (i + 1) < len(linePoints):
                cv2.line(frame, linePoints[i], linePoints[i + 1], (255, 0, 0), 1)

    if roi_wanted:
        if len(roi_points) >= 2 and roi_wanted and len(roi_points) % 2 == 0:
            x1, y1 = roi_points[-2][0], roi_points[-2][1]
            x2, y2 = roi_points[-1][0], roi_points[-1][1]
            # I noticed it made an unwanted output if the first value is not smaller
            if y1 > y2:
                y1, y2 = y2, y1
            if x1 > x2:
                x1, x2 = x2, x1

            part = frame[y1:y2, x1:x2]
            dim, part = scaled(part)
            frame[0:dim[1], 0:dim[0]] = part
            cv2.rectangle(frame, (0, 0), (dim[0] + 1, dim[1] + 1), (0, 0, 0), 2)


if __name__ == '__main__':
    if not (os.path.isdir('output_images&Videos')):  # to have an output folder ready
        os.mkdir('output_images&Videos')

    cap = cv2.VideoCapture(0)

    startedRec, record = False, False  # variable to know if the user started the recording or not

    out = None
    makeGray = False
    paused, pausedFrame = False, None

    try:  # this part is to save a variable in a file so the saved pics wont be overwritten
        f = open("output_images&Videos/imgCount&VidCount.txt", 'r')  # see if the folder exists take the variables
        print("read")
        imgNo = int(f.readline())
        videoNo = int(f.readline())
    except:
        imgNo = 0
        videoNo = 0
        f = open("output_images&Videos/imgCount&VidCount.txt",
                 'w')  # else make a new folder and initialize the variables
        f.write("0\n0")
    finally:
        f.close()

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:

            if paused:
                frame = pausedFrame

            if makeGray:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

            update_frame()

            if record:
                out.write(frame)

            cv2.imshow('frame', frame)

            cv2.setMouseCallback('frame', click_event)

            k = cv2.waitKey(1) & 0xFF

            if k == ord('q') or k == 27:
                f = open("output_images&Videos/imgCount&VidCount.txt", 'w')
                f.write(f"{imgNo}\n{videoNo}")
                f.close()
                break

            if k == ord('g'):  # convert to grey
                makeGray = True

            if k == ord('n'):  # convert to colored
                makeGray = False

            if k == ord('s'):  # save image
                cv2.imwrite(f'output_images&Videos/outputImg{imgNo}.jpg', frame)
                imgNo += 1
                print('Image Saved')

            if k == ord('v'):
                if not startedRec:
                    out = cv2.VideoWriter(f'output_images&Videos/outputVideo{videoNo}.avi',
                                          cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (frame.shape[1], frame.shape[0]))
                    record = True
                    startedRec = True
                    print("Started Recording")
                else:
                    print("Already Recording")

            if k == ord('b'):
                if record:
                    print("Recording Saved")
                    record = False
                    startedRec = False
                    videoNo += 1
                    out.release()
                    out = None
                else:
                    print("nothing to record")

            if k == ord('p'):
                if paused:
                    print('Already Paused')
                else:
                    paused = True
                    pausedFrame = frame

            if k == ord('o'):
                if paused:
                    paused = False
                else:
                    print("Image Already not Paused")

            if k == ord('t') and pointsEntered == 0:
                if pointsEntered == 0:
                    drawingMode = 't'
                    userWantToDraw = True

            if k == ord('c') and pointsEntered == 0:
                drawingMode = 'c'
                userWantToDraw = True

            if k == ord('l') and pointsEntered == 0:
                drawingMode = 'l'
                userWantToDraw = True

            if k == ord('i'):
                if roi_wanted:  # to close roi when clicked again
                    roi_wanted = False
                    roi_points.clear()
                    scale_percent = 100
                    continue

                if pointsEntered == 0:
                    drawingMode = 'i'
                    userWantToDraw = True
                    roi_wanted = True

            if k == ord('+'):
                if roi_wanted:
                    scale_percent += 10
            if k == ord('-'):
                if roi_wanted:
                    scale_percent -= 10

            if k == ord('r'):
                paused = False
                makeGray = False
                rectanglesPoints.clear()
                circlePoints.clear()
                linePoints.clear()

                drawingMode = None
                pointsEntered = 0
                userWantToDraw = False
                roi_points.clear()
                roi_wanted = False
                scale_percent = 100

        else:
            break

    cap.release()
    cv2.destroyAllWindows()
