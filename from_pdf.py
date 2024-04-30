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

input_file="C:\\Users\\ftheeten\\Downloads\\wetransfer_pna-nord_2024-04-30_0840\\PNA-NORD\\Parc_Albert_Nord (Virunga_Nord)_stations_cropped - Copy.pdf"
output_file="C:\\Users\\ftheeten\\Downloads\\wetransfer_pna-nord_2024-04-30_0840\\PNA-NORD\\Parc_Albert_Nord (Virunga_Nord)_stations_cropped_ocr_debug.pdf"
poppler_path="D:\\DEV\\CANATHIST\\POPPLER\\Release-24.02.0-0\\poppler-24.02.0\\Library\\bin"
tesseract_path="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
FONT_TO_PIXEL_RATIO=0.75


def go(p_input_file):
    global poppler_path
    global tesseract_path
    global FONT_TO_PIXEL_RATIO
    global output_file
    print(poppler_path)
    opacity=1.0
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    pdf_file = convert_from_path(p_input_file,poppler_path=poppler_path)
    color_transparent = Color( 0, 0, 0, alpha=opacity)
    output = PdfWriter()
    for (i,page) in enumerate(pdf_file) :
        print(i)
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
                
        can.setPageSize((math.floor(pdf_width), math.floor(pdf_height)))
        ratio_width=float(page_arr.shape[1]/pdf_width)
        ratio_height=float(page_arr.shape[0]/pdf_height)
        page_arr_gray = cv2.cvtColor(page_arr,cv2.COLOR_BGR2GRAY)        
      
        
        j=0
        #data = pytesseract.image_to_data(page_arr_gray, output_type='dict', config='-c preserve_interword_spaces=1')
        data = pytesseract.image_to_data(page_arr_gray, output_type='dict', config='--psm 6')
        print(data)
        sys.exit()
        for text in data["text"]:
            if len(text)>0:
                #print(text)
                font_size=data['height'][j]/ratio_height*FONT_TO_PIXEL_RATIO
                        
                can.setFont("Courier", font_size)
                can.drawString( (data['left'][j])/ratio_width, math.floor(pdf_height)-(data['top'][j]/ratio_height)-(data['height'][j]/ratio_height),text)
            j=j+1
        #cv2.imshow('image',page_arr_gray)
        #cv2.waitKey(0)
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
    output_stream = open(output_file, "wb")
    output.write(output_stream)
    output_stream.close()
go(input_file)