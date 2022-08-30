# @title: Hand Gesture detection algorithm
# @author: Sukru Erdem Gok
# win 10 
# python 3.8.3

import cv2
import mediapipe as mp
from os.path import exists

class HandRecognizer():
    def __init__(self, mode=False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands)
        self.mpDraw = mp.solutions.drawing_utils

        if not exists('gestures.txt'):
            f = open('gestures.txt', 'w')
            f.close()

    def find_hands(self, img):
        imgRBG = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRBG)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
            return (img, results.multi_hand_landmarks)

        return(img, {})#if there is no hand, return just empty dict

    def recognize_gesture(self, landmarks, tolerance):
        # locations of landmarks
        x_relations = []
        y_relations = []

        # dictionary which involves ids and locations
        x_dict = {}
        y_dict = {}

        if landmarks != {}:
            for landmark in landmarks:
                for id, lm in enumerate(landmark.landmark):
                    x_relations.append(lm.x)
                    y_relations.append(lm.y)

                    x_dict[lm.x] = id
                    y_dict[lm.y] = id

        # sort landmarks by locations
        x_relations.sort()
        y_relations.sort()

        x_ids = []
        y_ids = []

        for elem in x_relations:
            x_ids.append(x_dict[elem])

        for elem in y_relations:
            y_ids.append(y_dict[elem])

        file = open('gestures.txt', 'r')
        gestures_text = file.read()
        file.close()

        # saved gestures are seperated by /
        gestures_list = gestures_text.split('/')

        for gesture in gestures_list:
            if len(gesture) == 0:continue

            gesture_name = gesture.split('-')[0]

            gesture_x = gesture.split('-')[1].replace('[', '').replace(']', '').split(',')
            for elem in gesture_x:gesture_x[gesture_x.index(elem)] = int(elem.strip())

            gesture_y = gesture.split('-')[2].replace('[', '').replace(']', '').split(',')
            gesture_y.pop()# last one is empty
            for elem in gesture_y:gesture_y[gesture_y.index(elem)] = int(elem.strip())


            # get same ordered elements in saved gesture and camera capture
            same_elements_in_x = [i for i, j in zip(gesture_x, x_ids) if i == j]
            same_elements_in_y = [i for i, j in zip(gesture_y, y_ids) if i == j]

            # count of same ordered elements should be higher that these values
            min_x_val = len(gesture_x)-(tolerance/5)
            min_y_val = len(gesture_y)-(tolerance/5)

            if (len(same_elements_in_x) >= min_x_val and len(same_elements_in_y) >= min_y_val):
                print(gesture_name)
            else:print('-')

    def save_gesture(self, landmarks):
        x_relations = []
        y_relations = []

        x_dict = {}
        y_dict = {}

        if landmarks != {}:
            for landmark in landmarks:
                for id, lm in enumerate(landmark.landmark):
                    x_relations.append(lm.x)
                    y_relations.append(lm.y)

                    x_dict[lm.x] = id
                    y_dict[lm.y] = id

        x_relations.sort()
        y_relations.sort()

        x_ids = []
        y_ids = []

        for elem in x_relations:
            x_ids.append(x_dict[elem])

        for elem in y_relations:
            y_ids.append(y_dict[elem])

        gesture_name = input('gesture name: ')
        if gesture_name.strip() == 'exit':
            cap.release()
            exit()
        file = open('gestures.txt', 'a')
        file.write('{}-{}-{}/'.format(gesture_name, x_ids, y_ids))
        file.close()

if __name__ == '__main__':
    hr = HandRecognizer()
    cap = cv2.VideoCapture(0)

    while True:
        success,img = cap.read()

        img, landmarks = hr.find_hands(img)
        hr.recognize_gesture(landmarks, 65)
        cv2.imshow('img', img)

        if cv2.waitKey(1) == 27:hr.save_gesture(landmarks) # on esc save gesture, if input is exit, than exit