from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color

from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader
import cv2
import io
import numpy as np
import math
import pytesseract
import sys
import time
import pandas

input_file="C:\\DEV\\CANATHIST\\ocr_cedric\\Parc_Albert_Nord (Virunga_Nord)_stations_cropped - Copy.pdf"
output_file="C:\\DEV\\CANATHIST\\ocr_cedric\\Parc_Albert_Nord (Virunga_Nord)_stations_cropped_ocr.xlsx"
poppler_path="C:\\DEV\\CANATHIST\\tiff_to_ocr_pdf\\POPPLER\\Release-23.08.0-0\\poppler-23.08.0\\Library\\bin"
tesseract_path="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
FONT_TO_PIXEL_RATIO=0.75
treshold_block=400
min_size=8


def go(p_input_file):
    global poppler_path
    global tesseract_path
    global FONT_TO_PIXEL_RATIO
    global output_file
    global treshold_block
    global min_size
    print(poppler_path)
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    pdf_file = convert_from_path(p_input_file,poppler_path=poppler_path)
    desc_array={}
    for (i,page) in enumerate(pdf_file) :
        page_arr = np.asarray(page)
               
        page_arr_gray = cv2.cvtColor(page_arr,cv2.COLOR_BGR2GRAY)        
      
        
        j=0
        #data = pytesseract.image_to_data(page_arr_gray, output_type='dict', config='-c preserve_interword_spaces=1')
        data = pytesseract.image_to_data(page_arr_gray, output_type='dict', config='--psm 6 -c preserve_interword_spaces=1')
        print(data)
        
        NEW_BLOCK=True
        current_key="TITLE"
        
        desc_array[current_key]=[]
        last_left=0
        """
        for text in data["text"]:
            if len(text)>0:
                print(text)
                print(data["left"][j])
                current_left=data["left"][j]
                if current_left<last_left:
                    if current_left<treshold_block:
                        print("NEW_BLOCK")
                        NEW_BLOCK=True
                        
                        current_key=text
                        if current_key in desc_array:
                            current_key=current_key+ " duplicate ("+str(time.time())+")"
                        desc_array[current_key]=[]
                    #else: 
                    #    NEW_BLOCK=False
                    #    #print("NEW_LINE")
                else:
                    
                desc_array[current_key].append(text)
                last_left=current_left
            j=j+1
        break
        """
        new_entry=False
        for text in data["text"]:
            if len(text)>0:
                size=data["height"][j]
                if size>min_size:
                
                    print(text)
                    print(data["left"][j])
                    current_left=data["left"][j]
                    
                    if current_left<treshold_block or j==0:
                        print("NEW_BLOCK")
                        if new_entry==True:
                            current_key=current_key+ " "+text
                        else:
                            current_key=text
                        new_entry=True
                    else:
                        if new_entry==True:
                            if current_key in desc_array:
                                current_key=current_key+ " duplicate ("+str(time.time())+")"
                            desc_array[current_key]=[]
                            new_entry=False
                        if not current_key in desc_array:
                            desc_array[current_key]=[]
                        desc_array[current_key].append(text)
            j=j+1
        #break
    print(desc_array)
    final_text={}
    df = pandas.DataFrame()
    for key, items in desc_array.items():
        print(key)
        print(items)
        agg_text=' '.join(items)
        final_text[key]=agg_text
        obj={}
        obj["key"]=key
        if agg_text.startswith('='):
            agg_text="'"+agg_text
        obj["description"]=agg_text
        df= pandas.concat([df, pandas.DataFrame([obj])], ignore_index=True)
    print(final_text)
    df.to_excel(output_file)
    
go(input_file)