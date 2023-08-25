from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QSlider, QLabel, QLineEdit
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import traceback
import numpy as np
import sys

import cv2

app=None
window=None
layout=None

filename=None
image=None
display=None

lab_image=None
maxwidth, maxheight = 400, 500
currentwidth_truncate, currentheight_truncate=0,0
input_current_width=None
input_current_height=None
input_zoom=None
zoom_slider=None
ratio=0.0

slider_h_min=None
slider_s_min=None
slider_v_min=None
slider_h_max=None
slider_s_max=None
slider_v_max=None

input_h_min=None
input_s_min=None
input_v_min=None
input_h_max=None
input_s_max=None
input_v_max=None

h_min=None
s_min=None
v_min=None
h_max=None
s_max=None
v_max=None


def display_simple(ROI):
    global maxwidth
    global maxheight
    global zoom_factor
    global currentheight_truncate
    global currentwidth_truncate
    global ratio
    global input_zoom
    ref_height= ROI.shape[0]
    ref_width= ROI.shape[1]
    print(ref_height)
    print(ref_width)
    if ref_width>maxwidth:
        ratio=maxwidth/ref_width
        #print(ratio)
        
        #display_width=math.floor(ref_width/ratio)
        #print(maxheight)
        #print(display_width)
        #display = resize(ROI, (display_width, maxheight))
        display = cv2.resize(ROI, (0,0), fx=ratio, fy=ratio)        
        #PanZoomWindow(display,"test")
        cv2.imshow("",display)
        currentheight_truncate=display.shape[0]
        currentwidth_truncate=display.shape[1]
        
    else:
        #PanZoomWindow(ROI,"test")
        cv2.imshow("",ROI)
        ratio=1
        currentheight_truncate=ROI.shape[0]
        currentwidth_truncate=ROI.shape[1]
    input_zoom.setText(str(round(ratio,5)))
    zoom_slider.setValue(int(ratio*100))

def load_image(p_filename):     
    global image
    global display
    try:
        image =cv2.imread(p_filename)        
        display=image.copy()
        display_simple(display)
    except:    
        traceback.print_exception(*sys.exc_info())

        
        
def choose_tifs():
    global window
    file_c = QFileDialog()
    filter = "TIFF (*.TIF);;tiff (*.tif);;TIFF (*.TIFF);;tiff (*.tiff);;jpg (*.jpg);;jpg (*.JPG);;png (*.png);;png (*.PNG)"
    filename,_ = file_c.getOpenFileName(window, "Open files", "", filter)
    print(filename)
    load_image(filename)
  
def resize_image(ROI, ratio):
    global input_zoom
    global display
    ratio=ratio/100
    display = cv2.resize(ROI, (0,0), fx=ratio, fy=ratio)
    cv2.imshow("",display)
    input_zoom.setText(str(ratio))    
  
def slider_do_zoom():
    global zoom_slider
    global image
    resize_image(image, zoom_slider.value()) 
    
def slider_do_hsv():
    global display
    global slider_h_min
    global slider_s_min
    global slider_v_min
    global slider_h_max
    global slider_s_max
    global slider_v_max
    
    global input_h_min
    global input_s_min
    global input_v_min
    global input_h_max
    global input_s_max
    global input_v_max
    
    global h_min
    global s_min
    global v_min
    global h_max
    global s_max
    global v_max
    
    if slider_h_min is not None:
        h_min=slider_h_min.value()
        print(h_min)
        s_min=slider_s_min.value()
        v_min=slider_v_min.value()
        
        h_max=slider_h_max.value()
        s_max=slider_s_max.value()
        v_max=slider_v_max.value()
        
        input_h_min.setText(str(h_min))
        input_s_min.setText(str(s_min))
        input_v_min.setText(str(v_min))
        
        input_h_max.setText(str(h_max))
        input_s_max.setText(str(s_max))
        input_v_max.setText(str(v_max))
        
        # Set minimum and maximum HSV values to display
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        # Convert to HSV format and color threshold
        hsv = cv2.cvtColor(display, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        
        result = cv2.bitwise_and(display, display, mask=mask)
        
        cv2.imshow("",result)
    
    
    
    
    
def slider_hsv(p_layout, label_text, slider, input,  initial_value, max_level):
    tmp_label=QLabel(label_text)
    p_layout.addWidget(tmp_label)
    
    input.setText(str(initial_value))
    layout.addWidget(input)   

    slider.setFocusPolicy(Qt.StrongFocus)
    slider.setTickPosition(QSlider.TicksBothSides)
    slider.setTickInterval(10)
    slider.setSingleStep(1)
    slider.setRange(0, max_level)
    
    slider.setValue(initial_value)
    slider.valueChanged.connect(slider_do_hsv)
    p_layout.addWidget(slider)
    
def start():
    global app
    global window
    global layout
    
    global input_zoom
    global maxheight
    global maxwidth
    global zoom_slider
    
    global input_h_min
    global input_s_min
    global input_v_min
    global input_h_max
    global input_s_max
    global input_v_max
    
    global slider_h_min
    global slider_s_min
    global slider_v_min
    global slider_h_max
    global slider_s_max
    global slider_v_max
    try:
        app = QApplication([])
        window = QWidget()
        window.setMinimumWidth(700)
        
        layout = QVBoxLayout()
        
      
        
        but_tif=QPushButton('Select image file  :')
        layout.addWidget(but_tif)
        but_tif.clicked.connect(choose_tifs)
        
        lab_zoom=QLabel()
        lab_zoom.setText("Zoom level")
        layout.addWidget(lab_zoom)         
        
        
        input_zoom=QLineEdit()
        layout.addWidget(input_zoom)
        
        zoom_slider= QSlider(Qt.Horizontal)
        zoom_slider.setFocusPolicy(Qt.StrongFocus)
        zoom_slider.setTickPosition(QSlider.TicksBothSides)
        zoom_slider.setTickInterval(10)
        zoom_slider.setSingleStep(1)
        zoom_slider.setRange(1, 100)
        zoom_slider.valueChanged.connect(slider_do_zoom)
        layout.addWidget(zoom_slider)
        
        
        
        input_h_min=QLineEdit()
        slider_h_min=QSlider(Qt.Horizontal)
        slider_hsv(layout, "H Min",slider_h_min, input_h_min, 0, 179)
        
        input_s_min=QLineEdit()
        slider_s_min=QSlider(Qt.Horizontal)
        slider_hsv(layout, "S Min",slider_s_min, input_s_min, 0, 255)
        
        input_v_min=QLineEdit()
        slider_v_min=QSlider(Qt.Horizontal)
        slider_hsv(layout, "V Min",slider_v_min, input_v_min, 0, 255)
        
        input_h_max=QLineEdit()
        slider_h_max=QSlider(Qt.Horizontal)
        slider_hsv(layout, "H Max",slider_h_max, input_h_max, 179,179)
        
        input_s_max=QLineEdit()
        slider_s_max=QSlider(Qt.Horizontal)
        slider_hsv(layout, "S Max",slider_s_max, input_s_max, 255, 255)
        
        input_v_max=QLineEdit()
        slider_v_max=QSlider(Qt.Horizontal)
        slider_hsv(layout, "V Max",slider_v_max, input_v_max, 255, 255)
        
        
        
        
        
        
        
        window.setLayout(layout)
        window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        window.show()    
        app.exec()
        
    except:    
        traceback.print_exception(*sys.exc_info())
        
if __name__ == '__main__':
    start()