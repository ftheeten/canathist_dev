import traceback
import sys
import numpy as np
import cv2
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
import math
import re
import keras_ocr

global_rows=[]
#SRC_FILE="irscnb_d1684_012e6ex_1_corps-de-texte-red_wrk-10-15.pdf"
SRC_FILE="Capart_1955_Mission_De-Brouwer.pdf"
POPPLER_PATH="C:\\DEV\\CANATHIST\\tiff_to_ocr_pdf\\POPPLER\\Release-23.08.0-0\\poppler-23.08.0\\Library\\bin"


def display_with_factor(p_image, p_factor=0.5, window="", blocking=True):    
    cpy = cv2.resize(p_image, (0,0), fx=p_factor, fy=p_factor)
    cv2.imshow(window,cpy)
    if blocking:
        cv2.waitKey(0)
    

def extract_grid(image):
    # Load image, grayscale, Otsu's threshold
    display_with_factor(image, 0.5)
    '''
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    tesseract_list = pytesseract.image_to_data(gray, output_type='dict', config='-c preserve_interword_spaces=1')
    i=0
    for text in tesseract_list['text']:
        if len(text.strip())>0 and text.strip()!="|":
            x=tesseract_list['left'][i]
            y=tesseract_list['top'][i]
            w=tesseract_list['width'][i]
            h=tesseract_list['height'][i]
            ref_area=w*h
            cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 0)
        i=i+1
    display_with_factor(image,0.5)
    tesseract_list = pytesseract.image_to_data(gray, output_type='dict', config='digits')
    '''
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)

    display_with_factor(thresh)
    display_with_factor(dilate)
    display_with_factor(image)
    cv2.waitKey()
          
    
def start_ocr(p_input_file, page_begin, page_end,p_tesseract_path, p_poppler_mode=False, p_poppler_path=""):
    global global_rows
    pytesseract.pytesseract.tesseract_cmd =   p_tesseract_path 
    print("loaded")
    if p_poppler_mode:
        print(p_poppler_path)
        pdf_file = convert_from_path(p_input_file,poppler_path=p_poppler_path)
    else:
        pdf_file = convert_from_path(p_input_file)
    print("loaded")
    for (i,page) in enumerate(pdf_file) :            
        try:
            print("--------------------------------------------------------------------------")
            print("PAGE "+str(i))
            if i>=page_begin and i <=page_end:
                image_ori = np.asarray(page)
                #display_with_factor(image_ori, 0.33)            
                extract_grid(image_ori)
            
        except Exception as e2:
            traceback.print_exception(*sys.exc_info())
    print("DISPLAY")
    for row in global_rows:
        print(row)

print(cv2.__version__)

start_ocr(SRC_FILE, 1, 5,  "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")