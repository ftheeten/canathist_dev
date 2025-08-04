from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QSlider, QLabel, QLineEdit
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import traceback
import numpy as np
import sys
from pdf2image import convert_from_path
import cv2
import re
import os

POPPLER_PATH="D:\\DEV\\CANATHIST\\POPPLER\\Release-24.02.0-0\\poppler-24.02.0\\Library\\bin"


app=None
window=None
layout=None

filename=None
CURRENT_IMAGE=None
CURRENT_IMAGE_BEFORE_BORDER=None
CURRENT_HSV_IMAGE=None
CURRENT_LOWER_HSV=[]
CURRENT_UPPER_HSV=[]
display=None

lab_image=None
maxwidth, maxheight = 700, 1000
currentwidth_truncate, currentheight_truncate=0,0
input_current_width=None
input_current_height=None
input_zoom=None
zoom_slider=None
ratio=None

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

BORDER_UP=0
BORDER_DOWN=0
BORDER_LEFT=0
BORDER_RIGHT=0

input_border_top=None
input_border_bottom=None
input_border_left=None
input_border_right=None

lower_white=(0,0,230)
upper_white=(255,255,255)

CURRENT_PAGE=0
IMG_LIST=[]
lab_page=None
lab_folder=None

OUTPUT_FOLDER=[]

def reinit_hsv():
    global ratio
    global image
    global display
    global filename
    display=None
    print("reinit")
    print(ratio)
    display=None
    cv2.destroyWindow("")
    image=cv2.imread(filename)       
    display=image.copy()
    
    display = cv2.resize(display, (0,0), fx=ratio, fy=ratio)
    cv2.imshow("",display)
    
    
#def display_page(img, i_image)

def display_simple(ROI):
    global maxwidth
    global maxheight
    global zoom_factor
    global currentheight_truncate
    global currentwidth_truncate
    global ratio
    global input_zoom
    global display
    ref_height= ROI.shape[0]
    ref_width= ROI.shape[1]
    print(ref_height)
    print(ref_width)
    if ratio is None:
        if ref_height>maxwidth:
            ratio=maxwidth/ref_width
            if ref_height*ratio>maxheight:
                ratio=maxheight/ref_height
        #print(ratio)
        
        #display_width=math.floor(ref_width/ratio)
        #print(maxheight)
        #print(display_width)
        #display = resize(ROI, (display_width, maxheight))
        #ROI=cv2.cvtColor(ROI, cv2.COLOR_BGR2HSV)
        #ROI=cv2.cvtColor(ROI, cv2.COLOR_HSV2BGR)
    display = cv2.resize(ROI, (0,0), fx=ratio, fy=ratio)        
    #PanZoomWindow(display,"test")
    cv2.imshow("",display)
    currentheight_truncate=display.shape[0]
    currentwidth_truncate=display.shape[1]
    
    
    
    #else:
    #    #PanZoomWindow(ROI,"test")
    #    cv2.imshow("",ROI)
    #    ratio=1
    #    currentheight_truncate=ROI.shape[0]
    #    currentwidth_truncate=ROI.shape[1]
    input_zoom.setText(str(round(ratio,5)))
    zoom_slider.setValue(int(ratio*100))


def load_pdf(p_filename):
    global CURRENT_PAGE
    global lab_page
    global IMG_LIST
    IMG_LIST=[]
    CURRENT_PAGE=0
    pdf_file = convert_from_path(p_filename,poppler_path=POPPLER_PATH, dpi=600)
    
    for (i,page) in enumerate(pdf_file) :
        #cv2.imshow('image',page)
        #cv2.waitKey(0)
        print(i)
        page_arr = np.asarray(page)
        page_arr = cv2.cvtColor(page_arr,cv2.COLOR_BGR2RGB)
        IMG_LIST.append(page_arr)
    print("READY")
    lab_page.setText("Page"+str(CURRENT_PAGE+1)+"/"+str(len(IMG_LIST)))
    load_images()
 
def fnext():
    global CURRENT_PAGE
    global IMG_LIST
    global CURRENT_IMAGE
    global lab_page
    global display
    global ratio
    if CURRENT_PAGE<len(IMG_LIST):
        ratio=None
        CURRENT_PAGE=CURRENT_PAGE+1
        print(CURRENT_PAGE)
        CURRENT_IMAGE =IMG_LIST[CURRENT_PAGE]      
        display=CURRENT_IMAGE.copy()
        display_simple(display)
        apply_current_hsv()
        lab_page.setText("Page"+str(CURRENT_PAGE+1)+"/"+str(len(IMG_LIST)))        
        

def fprevious():
    global CURRENT_PAGE
    global IMG_LIST
    global CURRENT_IMAGE
    global lab_page
    global display
    global ratio
    if CURRENT_PAGE>0:
        ratio=None
        CURRENT_PAGE=CURRENT_PAGE-1
        print(CURRENT_PAGE)
        CURRENT_IMAGE =IMG_LIST[CURRENT_PAGE]      
        display=CURRENT_IMAGE.copy()
        display_simple(display)
        apply_current_hsv()
        lab_page.setText("Page"+str(CURRENT_PAGE+1)+"/"+str(len(IMG_LIST)))        
    

def fsave_hsv():
    global new_name
    global CURRENT_HSV_IMAGE
    global CURRENT_PAGE
    global CURRENT_LOWER_HSV
    global CURRENT_UPPER_HSV
    global filename
    global OUTPUT_FOLDER
    if len(OUTPUT_FOLDER)>0:
        hsv_full_image_job(CURRENT_LOWER_HSV, CURRENT_UPPER_HSV )    
        head, tail = os.path.split(filename)    
        new_name=tail.split(".")
        new_name=new_name[0]
        new_name=new_name+"_"+str(CURRENT_PAGE)+"_min_"+str(CURRENT_LOWER_HSV[0])+"_"+str(CURRENT_LOWER_HSV[1])"_"+str(CURRENT_LOWER_HSV[2])+"_max_"+str(CURRENT_UPPER_HSV[0])+"_"+str(CURRENT_UPPER_HSV[1])"_"+str(CURRENT_UPPER_HSV[2])+".tif"    
        new_name= os.path.join(OUTPUT_FOLDER[0], new_name)
        cv2.imwrite(new_name, CURRENT_HSV_IMAGE)
        print("saved "+new_name)
    
def load_images():    
    global CURRENT_PAGE
    global IMG_LIST
    global lab_page
    global CURRENT_IMAGE
    global display
    try:
        CURRENT_IMAGE =IMG_LIST[CURRENT_PAGE]  
        height, width, channels = CURRENT_IMAGE.shape
        print("height "+str(height))
        print("width "+str(width))        
        display=CURRENT_IMAGE.copy()
        display_simple(display)
        lab_page.setText("Page"+str(CURRENT_PAGE+1)+"/"+str(len(IMG_LIST)))
    except:    
        traceback.print_exception(*sys.exc_info())
   
        
def choose_pdf():
    global window
    global filename
    file_c = QFileDialog()
    filter = "PDF (*.PDF);;pdf (*.pdf)"
    filename,_ = file_c.getOpenFileName(window, "Open files", "", filter)
    print(filename)
    load_pdf(filename)
  
def resize_image(ROI, tmp):
    global input_zoom
    global display
    global ratio
    ratio=tmp/100
    display = cv2.resize(ROI, (0,0), fx=ratio, fy=ratio)
    cv2.imshow("",display)
    input_zoom.setText(str(ratio))    
  
def slider_do_zoom(val):
    global zoom_slider
    global CURRENT_IMAGE  
    resize_image(CURRENT_IMAGE, val) 
    
def hsv_full_image_job(p_lower_white, p_upper_white ):    
    global CURRENT_IMAGE
    global CURRENT_IMAGE_BEFORE_BORDER
    global CURRENT_HSV_IMAGE
    black_pixels_ori = np.where(
            (CURRENT_IMAGE[:, :, 0] == 0) & 
            (CURRENT_IMAGE[:, :, 1] == 0) & 
            (CURRENT_IMAGE[:, :, 2] == 0)
    )
    hsv = cv2.cvtColor(CURRENT_IMAGE, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, p_lower_white, p_upper_white)
        #mask = 255-mask
    mask=cv2.bitwise_not(mask)
    result = cv2.bitwise_and(CURRENT_IMAGE, CURRENT_IMAGE, mask=mask)
        
   
    #result[mask==0] = (255, 255, 255)
    black_pixels = np.where(
            (result[:, :, 0] == 0) & 
            (result[:, :, 1] == 0) & 
            (result[:, :, 2] == 0)
    )

    # set those pixels to white
    result[black_pixels] = [255, 255, 255]
    result[black_pixels_ori] = [0, 0, 0]
    CURRENT_HSV_IMAGE=result
    CURRENT_IMAGE_BEFORE_BORDER=CURRENT_HSV_IMAGE.copy()
    
def hsv_job(p_lower_white, p_upper_white ):
    global display
    black_pixels_ori = np.where(
            (display[:, :, 0] == 0) & 
            (display[:, :, 1] == 0) & 
            (display[:, :, 2] == 0)
    )
    hsv = cv2.cvtColor(display, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, p_lower_white, p_upper_white)
        #mask = 255-mask
    mask=cv2.bitwise_not(mask)
    result = cv2.bitwise_and(display, display, mask=mask)
        
    # set those pixels to white
    #result[black_pixels] = [255, 255, 255]
        
    #result = imgcopy.copy()
    #result[mask==0] = (255, 255, 255)
    black_pixels = np.where(
            (result[:, :, 0] == 0) & 
            (result[:, :, 1] == 0) & 
            (result[:, :, 2] == 0)
    )

    # set those pixels to white
    result[black_pixels] = [255, 255, 255]
    result[black_pixels_ori] = [0, 0, 0]
    cv2.imshow("",result)
    
def slider_do_hsv():
    
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
    
    global CURRENT_LOWER_HSV
    global CURRENT_UPPER_HSV
    
    if slider_h_min is not None:
        
        h_min=slider_h_min.value()
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
        CURRENT_LOWER_HSV=lower
        CURRENT_UPPER_HSV=upper
        hsv_job(lower, upper)
        # Convert to HSV format and color threshold
        
    
    
def preset_white_hsv():
    global lower_white
    global upper_white
    slider_h_min.setValue(lower_white[0])
    slider_s_min.setValue(lower_white[1])
    slider_v_min.setValue(lower_white[2])
        
    slider_h_max.setValue(upper_white[0])
    slider_s_max.setValue(upper_white[1])
    slider_v_max.setValue(upper_white[2])
    
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
    
def choose_output():
    global OUTPUT_FOLDER
    global lab_folder
    folders_output=[]
    file= QFileDialog.getExistingDirectory(window, "Choose folder to add")
    OUTPUT_FOLDER=[file]
    lab_folder.setText("Output folder "+str(OUTPUT_FOLDER[0]))
  
def draw_border():
    global input_border_top
    global input_border_bottom
    global input_border_left
    global input_border_right
    global CURRENT_HSV_IMAGE  
    global CURRENT_IMAGE_BEFORE_BORDER
    global display
    
    if CURRENT_IMAGE_BEFORE_BORDER is not None:
        CURRENT_HSV_IMAGE=CURRENT_IMAGE_BEFORE_BORDER
    
        
    height, width, channels = CURRENT_HSV_IMAGE.shape
    
    color = (255, 255, 255)
    input_top=int(input_border_top.text())
    input_left=int(input_border_left.text())
    input_bottom=int(input_border_bottom.text())
    input_right=int(input_border_right.text())
    if input_top>0:
        start_point_top=(0,0)
        end_point_top=(width, input_top)
        #print("top")
        #print(start_point_top)
        #print(start_point_top)
        CURRENT_HSV_IMAGE = cv2.rectangle(CURRENT_HSV_IMAGE, start_point_top, end_point_top, color, -1) 
    if input_left>0:
        start_point_left=(0,0)        
        end_point_left=(input_left, height)
        #print("left")
        #print(start_point_left)
        #print(end_point_left)
        CURRENT_HSV_IMAGE = cv2.rectangle(CURRENT_HSV_IMAGE, start_point_left, end_point_left, color, -1)
    if input_bottom>0:        
        start_point_bottom=(0,height-input_bottom)
        end_point_bottom=(width, height)
        #print("bottom")
        #print(start_point_bottom)
        #print(end_point_bottom)        
        CURRENT_HSV_IMAGE = cv2.rectangle(CURRENT_HSV_IMAGE, start_point_bottom, end_point_bottom,  color, -1) 
    if input_right>0:        
        start_point_right=(width-input_right,0)
        end_point_right=(width, height)
        #print("right")
        #print(start_point_right)
        #print(end_point_right)
        CURRENT_HSV_IMAGE = cv2.rectangle(CURRENT_HSV_IMAGE, start_point_right, end_point_right, color, -1)        
    display=CURRENT_HSV_IMAGE.copy()
    display_simple(display)
    
def apply_current_hsv():
    global CURRENT_LOWER_HSV
    global CURRENT_UPPER_HSV  
    global CURRENT_IMAGE
    global lower_white
    global upper_white
    height, width, channels = CURRENT_IMAGE.shape
    print("height "+str(height))
    print("width "+str(width))
    if CURRENT_LOWER_HSV is None:
        CURRENT_LOWER_HSV=[]
    if CURRENT_UPPER_HSV is None:
        CURRENT_UPPER_HSV=[]
    if len(CURRENT_LOWER_HSV)==0:
        CURRENT_LOWER_HSV=lower_white
    if len(CURRENT_UPPER_HSV)==0:
        CURRENT_UPPER_HSV=upper_white
    
    hsv_job(CURRENT_LOWER_HSV, CURRENT_UPPER_HSV)
    hsv_full_image_job(CURRENT_LOWER_HSV, CURRENT_UPPER_HSV )
    draw_border()
    
def start():
    global app
    global window
    global layout
    
    global input_zoom
    global lab_page
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
    
    global lab_folder
    
    global BORDER_UP
    global BORDER_DOWN
    global BORDER_LEFT
    global BORDER_RIGHT
    
    global input_border_top
    global input_border_bottom
    global input_border_left
    global input_border_right
    
    global lower_white
    global upper_white
    
    try:
        app = QApplication([])
        window = QWidget()
        window.setMinimumWidth(700)
        
        layout = QVBoxLayout()
        
      
        
        but_pdf=QPushButton('Select PDF file  :')
        layout.addWidget(but_pdf)
        but_pdf.clicked.connect(choose_pdf)
        
        
        
        but_output=QPushButton('Choose output image folder')
        layout.addWidget(but_output)
        but_output.clicked.connect(choose_output)
        
        lab_folder=QLabel()
        layout.addWidget(lab_folder)
        
        but_previous=QPushButton('<<')
        layout.addWidget(but_previous)
        but_previous.clicked.connect(fprevious)
        
        but_next=QPushButton('>>')
        layout.addWidget(but_next)
        but_next.clicked.connect(fnext)
        
        but_save_hsv=QPushButton('Save HSV IMAGE')
        layout.addWidget(but_save_hsv)
        but_save_hsv.clicked.connect(fsave_hsv)
        
        lab_page=QLabel()
        lab_page.setText("Page")
        layout.addWidget(lab_page)  
        
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
        slider_hsv(layout, "H Min",slider_h_min, input_h_min, lower_white[0], 179)
        
        input_s_min=QLineEdit()
        slider_s_min=QSlider(Qt.Horizontal)
        slider_hsv(layout, "S Min",slider_s_min, input_s_min, lower_white[1], 255)
        
        input_v_min=QLineEdit()
        slider_v_min=QSlider(Qt.Horizontal)
        slider_hsv(layout, "V Min",slider_v_min, input_v_min, lower_white[2], 255)
        
        input_h_max=QLineEdit()
        slider_h_max=QSlider(Qt.Horizontal)
        slider_hsv(layout, "H Max",slider_h_max, input_h_max, upper_white[0],179)
        
        input_s_max=QLineEdit()
        slider_s_max=QSlider(Qt.Horizontal)
        slider_hsv(layout, "S Max",slider_s_max, input_s_max, upper_white[1], 255)
        
        input_v_max=QLineEdit()
        slider_v_max=QSlider(Qt.Horizontal)
        slider_hsv(layout, "V Max",slider_v_max, input_v_max, upper_white[2], 255)
        
        
        
        
        lab_border_top=QLabel()
        lab_border_top.setText("Border top")
        layout.addWidget(lab_border_top)      
        
        input_border_top=QLineEdit()
        input_border_top.setText(str(BORDER_UP))
        layout.addWidget(input_border_top)
        
        lab_border_bottom=QLabel()
        lab_border_bottom.setText("Border bottom")
        layout.addWidget(lab_border_bottom)  
        
        input_border_bottom=QLineEdit()
        input_border_bottom.setText(str(BORDER_DOWN))
        layout.addWidget(input_border_bottom)
        
        lab_border_left=QLabel()
        lab_border_left.setText("Border left")
        layout.addWidget(lab_border_left)  
        
        input_border_left=QLineEdit()
        input_border_left.setText(str(BORDER_LEFT))
        layout.addWidget(input_border_left)
        
        lab_border_right=QLabel()
        lab_border_right.setText("Border right")
        layout.addWidget(lab_border_right)  
        
        input_border_right=QLineEdit()
        input_border_right.setText(str(BORDER_RIGHT))
        layout.addWidget(input_border_right)
        
        but_appy=QPushButton('Apply')
        layout.addWidget(but_appy)
        but_appy.clicked.connect(apply_current_hsv)
        
        but_whitepreset=QPushButton('White preset  :')
        layout.addWidget(but_whitepreset)
        but_whitepreset.clicked.connect(preset_white_hsv)
        
        but_reset=QPushButton('Reset HSV  :')
        layout.addWidget(but_reset)
        but_reset.clicked.connect(reinit_hsv)
        
        window.setLayout(layout)
        window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        window.show()    
        app.exec()
        
    except:    
        traceback.print_exception(*sys.exc_info())
        
if __name__ == '__main__':
    print("go")
    start()