import cv2
from tensorflow import keras
# from tensorflow.keras.models import load_model
from PIL import Image, ImageTk
import tkinter as tk
# import cv2
import os
import numpy as np
import operator
import time
import sys, os
import matplotlib.pyplot as plt
from string import ascii_uppercase
from spellchecker import SpellChecker

class Application:
    def __init__(self):
        # self.model = load_model('model.h5')
        self.model = keras.models.load_model('model.h5')
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        self.speller = SpellChecker()
        self.frame_count = 0

        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        for i in ascii_uppercase:
          self.ct[i] = 0
        print("Loaded model from disk")

        self.root = tk.Tk()
        self.root.title("Sign language to Text Converter")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.geometry("1250x600")

        self.panel = tk.Label(self.root)
        self.panel.place(x = 50, y = 10, width = 500, height = 450)

        self.panel2 = tk.Label(self.root)  # initialize image panel
        self.panel2.place(x=300, y=47, width=275, height=275)

        self.T = tk.Label(self.root)
        self.T.place(x=20, y=5)
        self.T.config(text="Sign Language To Text Conversion", font=("Courier", 24, "bold"))

        self.photosign = tk.PhotoImage(file='pics/signs.png')
        self.w6 = tk.Label(self.root, image=self.photosign)
        self.w6.place(x=600, y=60)
        self.tx6 = tk.Label(self.root)
        self.tx6.place(x=700, y=5)
        self.tx6.config(text="Sign Languages",
                        font=("Courier", 22, "bold"))

        self.panel3 = tk.Label(self.root)  # Current Symbol
        self.panel3.place(x=200, y=460)

        self.T1 = tk.Label(self.root)
        self.T1.place(x=10, y=460)
        self.T1.config(text="Character :", font=("Courier", 18, "bold"))

        self.panel4 = tk.Label(self.root)  # Word
        self.panel4.place(x=200, y=490)
        self.T2 = tk.Label(self.root)
        self.T2.place(x=10, y=490)
        self.T2.config(text="Word :", font=("Courier", 18, "bold"))

        self.bt1=tk.Button(self.root, command=self.action1,height = 0,width = 0)
        self.bt1.place(x = 26,y=890)
        #self.bt1.grid(padx = 10, pady = 10)
        self.bt2=tk.Button(self.root, command=self.action2,height = 0,width = 0)
        self.bt2.place(x = 325,y=890)
        #self.panel3.place(x = 10,y=660)
        # self.bt2.grid(row = 4, column = 1, columnspan = 1, padx = 10, pady = 10, sticky = tk.NW)
        self.bt3=tk.Button(self.root, command=self.action3,height = 0,width = 0)
        self.bt3.place(x = 625,y=890)
        # self.bt3.grid(row = 4, column = 2, columnspan = 1, padx = 10, pady = 10, sticky = tk.NW)
        self.bt4=tk.Button(self.root, command=self.action4,height = 0,width = 0)
        self.bt4.place(x = 125,y=950)
        # self.bt4.grid(row = bt1, column = 0, columnspan = 1, padx = 10, pady = 10, sticky = tk.N)
        self.bt5=tk.Button(self.root, command=self.action5,height = 0,width = 0)
        self.bt5.place(x = 425,y=950)
        # self.bt5.grid(row = 5, column = 1, columnspan = 1, padx = 10, pady = 10, sticky = tk.N)
        self.str=""
        self.word=""
        self.current_symbol="Empty"
        self.photo="Empty"
        self.video_loop()

    def video_loop(self):
        ok, frame = self.vs.read()
        if ok:
            self.frame_count += 1
            cv2image = cv2.flip(frame, 1)
            x1 = int(0.5*frame.shape[1])
            y1 = 10
            x2 = frame.shape[1]-10
            y2 = int(0.5*frame.shape[1])
            cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGB)

            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

            im = Image.fromarray(frame, 'RGB')

            img_array = np.asarray(frame)

            clone = img_array[25:250, 25:250].copy()

            if self.frame_count % 50 == 0:
                self.predict(clone)
            self.current_image2 = Image.fromarray(clone)
            imgtk = ImageTk.PhotoImage(image=self.current_image2)

            self.panel2.imgtk = imgtk
            self.panel2.config(image=imgtk)
            self.panel3.config(text=self.current_symbol,font=("Courier",18))
            self.panel4.config(text=self.word,font=("Courier",18))

            predicts=self.speller.correction(self.word)

            if(len(predicts) > 0):
                self.bt1.config(text=predicts[0],font = ("Courier",20))
            else:
                self.bt1.config(text="")
            if(len(predicts) > 1):
                self.bt2.config(text=predicts[1],font = ("Courier",20))
            else:
                self.bt2.config(text="")
            if(len(predicts) > 2):
                self.bt3.config(text=predicts[2],font = ("Courier",20))
            else:
                self.bt3.config(text="")
            if(len(predicts) > 3):
                self.bt4.config(text=predicts[3],font = ("Courier",20))
            else:
                self.bt4.config(text="")
            if(len(predicts) > 4):
                self.bt4.config(text=predicts[4],font = ("Courier",20))
            else:
                self.bt4.config(text="")
        self.root.after(30, self.video_loop)
    def predict(self,clone):
        clone_resized = cv2.resize(clone, (64, 64))

        img_array = clone_resized / 255

        img_final = np.expand_dims(img_array, axis=0)

        prediction = self.model.predict(img_final)

        label = np.argmax(prediction)

        if label == 27 or label == 26:
            self.current_symbol = ''
        elif label == 28:
            self.current_symbol = ' '
        else:
            self.current_symbol = chr(ord('A') + label)

        self.word += self.current_symbol

    def action1(self):
        predicts=self.speller.correction(self.word)
        if(len(predicts) > 0):
            self.word=""
            self.str+=" "
            self.str+=predicts[0]

    def action2(self):
        predicts=self.speller.correction(self.word)
        if(len(predicts) > 1):
            self.word=""
            self.str+=" "
            self.str+=predicts[1]

    def action3(self):
        predicts=self.speller.correction(self.word)
        if(len(predicts) > 2):
            self.word=""
            self.str+=" "
            self.str+=predicts[2]

    def action4(self):
        predicts=self.speller.correction(self.word)
        if(len(predicts) > 3):
            self.word=""
            self.str+=" "
            self.str+=predicts[3]

    def action5(self):
        predicts=self.speller.correction(self.word)
        if(len(predicts) > 4):
            self.word=""
            self.str+=" "
            self.str+=predicts[4]

    def destructor(self):
        print("Closing Application...")
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()
    
    def destructor1(self):
        print("Closing Application...")
        self.root1.destroy()

print("Starting Application...")
pba = Application()
pba.root.mainloop()
