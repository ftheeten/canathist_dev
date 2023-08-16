#https://medium.com/social-impact-analytics/extract-text-from-unsearchable-pdfs-for-data-analysis-using-python-a6a2ca0866dd

# import libs
try:
    from PIL import Image
except ImportError:
    import Image
import cv2
import pytesseract
import os
import numpy as np
import pandas as pd
import re
from pdf2image import convert_from_bytes, convert_from_path
import traceback
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
import cv2
from reportlab.lib.units import mm
from reportlab.lib.colors import Color
import math
import io


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


  


def ocr_extract(p_files, p_o_files):
    OCR_dic={}
    main_i=0
    color_transparent = Color( 0, 0, 0, alpha=0.0)    
    for file in p_files:
        
        print(file)
        pdf_file = convert_from_path(file)
        output_file=p_o_files[main_i]
        output = PdfWriter()
        for (i,page) in enumerate(pdf_file) :
            
            existing_pdf = PdfReader(open(file, "rb"))
            
            packet = io.BytesIO()
            try:
                print(i)
                
                box = existing_pdf.pages[i].mediabox
                #print(box)
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
                #print(ratio_width)
                #print(ratio_height)
                
                page_arr_gray = cv2.cvtColor(page_arr,cv2.COLOR_BGR2GRAY)
                data = pytesseract.image_to_data(page_arr_gray, output_type='dict')
                #print(text)
                j=0
              
                for text in data["text"]:
                    if len(text)>0:
                        #print(text)
                        #print(data['left'][j])
                        #print(data['top'][j])
                        can.drawString( (data['left'][j])/ratio_width, math.floor(pdf_height)-(data['top'][j]/ratio_height),text)
                    j=j+1
                #print(len(data["text"]))
                #print(len(data["top"]))
                #print(len(data["left"]))
                
                can.save()
                packet.seek(0)
                new_pdf = PdfReader(packet)
                page_ori = existing_pdf.pages[i]
                page_ori.merge_page(new_pdf.pages[0])
                output.add_page(page_ori)
            except:
                traceback.print_exc()
                # if can't extract then give some notes into df
                #pages_df = pages_df.append({'conf': -1,'text': 'N/A'}, ignore_index=True)
        output_stream = open(output_file, "wb")
        output.write(output_stream)
        output_stream.close()
        main_i=main_i+1

files=["D:\\DEV\\CANATHIST\\test_pdf_ocr_larissa\\Ann.Mus.Terv.in-8o.Zool.001-11-40.pdf"]
files_with_text=["D:\\DEV\\CANATHIST\\test_pdf_ocr_larissa\\Ann.Mus.Terv.in-8o.Zool.001-11-40_text.pdf"]
ocr_extract(files, files_with_text)