from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel
from PySide6.QtCore import Qt
import os
import io
import traceback
import sys

import configparser

import cv2
import pytesseract
import numpy as np
import math

#from PIL import Image

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color

from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader

from datetime import datetime



app=None
window=None
console=None
filenames=[]
output_pdf_file=None
input_height=None
input_tesseract=None

CONFIG_FILE="config.cfg"
TESSERACT_PATH=""
USER_TESSERACT_PATH=""

HEIGHT_IMAGE_CM=""
USER_HEIGHT_IMAGE_CM=""
USER_HEIGHT_IMAGE_PX=""
PIXEL_PER_CM=""



def display_time():
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")    
    print("date and time:",date_time)
 

def resize_image_target_height( image):    
    
    global USER_HEIGHT_IMAGE_PX
    width_image=image.shape[1]
    height_image=image.shape[0]
    current_height_ratio=USER_HEIGHT_IMAGE_PX/height_image
    return current_height_ratio
    

def ocr_extract(p_input_file):
    global console
    try:
        print("loading file...")
        display_time()
        #file=p_input_file
        pdf_file = convert_from_path(p_input_file)
        output_file=p_input_file
        output = PdfWriter()
        print("file loaded")
        display_time()
        color_transparent = Color( 0, 0, 0, alpha=0.0)
        for (i,page) in enumerate(pdf_file) :            
            try:
                if (i+1)%10==0:
                    print("page "+str(i+1)+"/"+str(len(pdf_file)))
                    display_time()
                
                existing_pdf = PdfReader(open(p_input_file, "rb"))
                packet = io.BytesIO()
                box = existing_pdf.pages[i].mediabox
                min_pt = box.lower_left
                max_pt = box.upper_right
                pdf_width = max_pt[0] - min_pt[0]
                pdf_height = max_pt[1] - min_pt[1]
                page_arr = np.asarray(page)
                can = canvas.Canvas(packet)
                can.setFillColor(color_transparent)
                can.setFont("Courier", 6)
                can.setPageSize((math.floor(pdf_width), math.floor(pdf_height)))
                ratio_width=float(page_arr.shape[1]/pdf_width)
                ratio_height=float(page_arr.shape[0]/pdf_height)
                page_arr_gray = cv2.cvtColor(page_arr,cv2.COLOR_BGR2GRAY)
                data = pytesseract.image_to_data(page_arr_gray, output_type='dict', config='-c preserve_interword_spaces=1')                
                j=0
                for text in data["text"]:
                    if len(text)>0:
                        can.drawString( (data['left'][j])/ratio_width, math.floor(pdf_height)-(data['top'][j]/ratio_height),text)
                    j=j+1
                can.save()
                packet.seek(0)
                new_pdf = PdfReader(packet)
                page_ori = existing_pdf.pages[i]
                page_ori.merge_page(new_pdf.pages[0])
                output.add_page(page_ori)        
                existing_pdf=None
                new_pdf=None
                can=None
                packet=None
            except Exception as e2:
                s = str(e2)
                print("\r\nError: "+s)
        output_stream = open(output_file, "wb")
        output.write(output_stream)
        output_stream.close()
        
        pdf_file=None
        print("done (intermediate pdf conversion)")
        print("Next step is OCR")
        display_time()
    except Exception as e1:
        s = str(e1)
        print("\r\nError: "+s)
 
def generate_pdf(p_input_files, p_output_file):
    try:
        print("generating  temporary PDF")
        print("loading file...")
        display_time()
        can = canvas.Canvas(p_output_file)
        p_input_files.sort()
        print("nb pages="+str(len(p_input_files)))
        for i, image_path in enumerate(p_input_files):
            #print(i)
            if (i+1)%10==0:
                print("page (intermediate PDF) "+str(i+1)+"/"+str(len(p_input_files)))
                display_time()
            image =  cv2.imread(image_path)
            size_ratio=resize_image_target_height( image)
            can.setPageSize((image.shape[1]*size_ratio,image.shape[0]*size_ratio))
            
            page_arr_gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            
            can.drawImage(image_path, 0, 0, width=image.shape[1]*size_ratio, height=image.shape[0]*size_ratio)            
            can.showPage()
        can.save()
        can=None
        print("Done")
        display_time()    
    except:    
        traceback.print_exception(*sys.exc_info())
    

    
def lauch_ocr(p_file):
    global window
    global console
    console.setText("processing \r\n"+p_file)

def choose_tifs(x):
    global window
    global filenames
    console.setText("Tiffs")
    file_name = QFileDialog()
    filter = "TIFF (*.TIF);;tiff (*.tif);;TIFF (*.TIFF);;tiff (*.tiff)"
    filenames, _ = file_name.getOpenFileNames(window, "Open files", "", filter)
    
def choose_output():
    global window
    global output_pdf_file
    global console
    global filenames
    folder_object = QFileDialog()
    if len(filenames)>0:
        output_pdf_file =folder_object.getSaveFileName(window, dir=os.path.dirname(filenames[0])+".pdf",  caption='Select a data file', filter='PDF File (*.pdf)')[0]
    else:
        output_pdf_file =folder_object.getSaveFileName(window, caption='Select a data file', filter='PDF File (*.pdf)')[0]
    console.setText(console.text()+"\r\nOutput file: "+output_pdf_file)

def launch_ocr():
    global window
    global filenames
    global output_pdf_file
    global console
    global input_height
    global input_tesseract
    global USER_HEIGHT_IMAGE_CM
    global USER_HEIGHT_IMAGE_PX
    global PIXEL_PER_CM
    global USER_TESSERACT_PATH

    
    if output_pdf_file is None or filenames is None:
        console.setText(console.text()+"\r\nPDF files and/or Output folder not set")
        print("PDF files and/or Output folder not set")
    else:
        i=0
        USER_HEIGHT_IMAGE_CM=float(input_height.text())
        USER_HEIGHT_IMAGE_PX=USER_HEIGHT_IMAGE_CM*float(PIXEL_PER_CM)
        
        print("user height "+str(USER_HEIGHT_IMAGE_CM)+"cm")
        print("user height "+str(USER_HEIGHT_IMAGE_PX)+"pixels")
        temp=output_pdf_file
        generate_pdf(filenames, temp)
        ocr_extract(temp)        

        print("DONE FOR "+output_pdf_file)
        display_time()
    print("PENDING (Ready)")
    
def choose_tesseract():
    global window
    global USER_TESSERACT_PATH
    global input_tesseract
    file_name = QFileDialog()
    filter = "exe (*.exe);;exe (*.EXE)"
    USER_TESSERACT_PATH,_ = file_name.getOpenFileName(window, "Open files", "", filter)
    print(USER_TESSERACT_PATH)
    if os.path.isfile(USER_TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = USER_TESSERACT_PATH
        print("TESSERACT ON "+ USER_TESSERACT_PATH)
        input_tesseract.setText(USER_TESSERACT_PATH)
        pytesseract.pytesseract.tesseract_cmd = USER_TESSERACT_PATH
    else:
        print("TESSERACT NOT FOUND - SET IT MANUALLY !!!!")
    
def start():
    global app
    global window
    global CONFIG_FILE
    global TESSERACT_PATH
    global USER_TESSERACT_PATH
    global PIXEL_PER_CM
    global console
    global input_height
    global input_tesseract

    
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        TESSERACT_PATH=config["SYSTEM"]["tesseract_path"]
        HEIGHT_IMAGE_CM=config["OUTPUT"]["height_image_cm"]
        PIXEL_PER_CM=config["OUTPUT"]["pixel_per_cm"]
        
        USER_TESSERACT_PATH=TESSERACT_PATH.replace("\\","/").replace("'","").replace('"','').strip()
        if os.path.isfile(USER_TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = USER_TESSERACT_PATH
            print("TESSERACT ON "+ USER_TESSERACT_PATH)
        else:
            print("TESSERACT NOT FOUND - SET IT MANUALLY !!!!")
        app = QApplication([])
        window = QWidget()
        window.setMinimumWidth(700)
        
        layout = QVBoxLayout()
        
        lab_tesseract=QLabel()
        lab_tesseract.setText("Tesseract path")
        layout.addWidget(lab_tesseract)
        
        input_tesseract=QLabel()
        input_tesseract.setText(TESSERACT_PATH)
        layout.addWidget(input_tesseract)
        
        
        
        but_tif=QPushButton('Choose source Tifs')
        layout.addWidget(but_tif)
        but_tif.clicked.connect(choose_tifs)
        
        but_output=QPushButton('Create output PDF')
        layout.addWidget(but_output)
        but_output.clicked.connect(choose_output)
        
        window.setLayout(layout)
        window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        window.show()    
        
        lab_height=QLabel()
        lab_height.setText("Height page (cm)")
        layout.addWidget(lab_height)
        
        input_height=QLineEdit()
        input_height.setText(HEIGHT_IMAGE_CM)
        layout.addWidget(input_height)
        
        but_change_tesseract=QPushButton('Change tesseract')
        layout.addWidget(but_change_tesseract)
        but_change_tesseract.clicked.connect(choose_tesseract)
        
        but_launch=QPushButton('Launch OCR')
        layout.addWidget(but_launch)
        but_launch.clicked.connect(launch_ocr)
        
        
        
        console=QLabel()
        console.setText("Output")
        layout.addWidget(console)
        app.exec()
    except:    
        traceback.print_exception(*sys.exc_info())
if __name__ == '__main__':
    start()