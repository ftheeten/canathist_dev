#https://medium.com/social-impact-analytics/extract-text-from-unsearchable-pdfs-for-data-analysis-using-python-a6a2ca0866dd

# import libs
try:
    from PIL import Image
except ImportError:
    import Image
import matplotlib.pyplot as plt
import keras_ocr
import os
import numpy as np
import re
import io
from pdf2image import convert_from_bytes, convert_from_path
import traceback
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import letter
import cv2
from reportlab.lib.units import mm
import math




def ocr_extract(p_files, p_o_files):
    pipeline = keras_ocr.pipeline.Pipeline()
    OCR_dic={} 
    main_i=0
    for file in p_files:
        output_file=p_o_files[main_i]
        
        # convert pdf into image
        #pdf=open(file)
        existing_pdf = PdfReader(open(file, "rb"))
        
        output = PdfWriter()
        packet = io.BytesIO()
        print(file)
        print(output_file)
        pdf_file = convert_from_path(file)
        # create a df to save each pdf's text
        for (i,page) in enumerate(pdf_file) :
            try:
                print(i)
                box = existing_pdf.pages[i].mediabox
                print(box)
                # 1 user space unit is 1/72 inch
                # 1/72 inch ~ 0.352 millimeters
                page_arr = np.asarray(page)
                #page_arr_gray = cv2.cvtColor(page_arr,cv2.COLOR_BGR2GRAY)
                print(page_arr.shape)
                min_pt = box.lower_left
                max_pt = box.upper_right
                pdf_width = max_pt[0] - min_pt[0]
                pdf_height = max_pt[1] - min_pt[1]
                print(pdf_width)
                print(pdf_height)
                
                can = canvas.Canvas(packet)
                #can.setPageSize((page_arr.shape[1], page_arr.shape[0])) 
                can.setPageSize((math.floor(pdf_width), math.floor(pdf_height)))
                print(page_arr.shape)
                ratio_width=float(page_arr.shape[1]/pdf_width)
                ratio_height=float(page_arr.shape[0]/pdf_height)
                print(ratio_width)
                print(ratio_height)
                #break
                file_handler=keras_ocr.tools.read(page_arr)
                prediction_obj = pipeline.recognize([file_handler])[0]
                #fig, axs = plt.subplots(nrows=len([file_handler]), figsize=(20, 20))
                print(prediction_obj)
                #print(fig)
                #print(axs)
                
                j=0
                previoux_x=0
                previoux_y=0
                line_content=[]
                textobject = can.beginText()
                last_word=len(prediction_obj)
                print(last_word)
                is_new_line=True
                begin_line=0
                print(predictions)
                print(type(prediction).__name__)
                """
                for prediction in prediction_obj:
                    
                    #print(type(prediction).__name__)
                    #print(prediction)
                    #print(prediction[0])
                    #print(prediction[1])
                    text=prediction[0]
                    x=math.floor(float(prediction[1][0][0])/ratio_width)
                    y=math.floor(float(prediction[1][0][1])/ratio_height)
                    if is_new_line:
                        begin_line=x
                        is_new_line=False
                    #print(text)
                    #print(x)
                    #print(y)
                    #break
                    line_content.append(text)
                    if y<previoux_y or j==(last_word-1):
                        print("NEW_LINE")
                        print(' '.join(line_content))
                        textobject.setTextOrigin(begin_line, math.floor(pdf_height)-previoux_x)
                        textobject.textLine(text=' '.join(line_content))
                        can.drawText(textobject)
                        line_content=[]
                        if(j<last_word-1):
                            textobject = can.beginText()
                        is_new_line=True
                    previoux_x=x
                    previoux_y=y
                    
                    j=j+1
                    
                    
                    
                
                can.save()
                packet.seek(0)
                new_pdf = PdfReader(packet)
                page_ori = existing_pdf.pages[i]
                page_ori.merge_page(new_pdf.pages[0])
                output.add_page(page_ori)
                
                
                #for ax, image, predictions in zip(axs, [file_handler], prediction_obj):
                #    keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
                
                #cv2.imshow('image',page_arr_gray)
                #cv2.waitKey(0)
                '''
                page_deskew = deskew(page_arr_gray)
                cv2.imshow('image',page_deskew)
                cv2.waitKey(0)
                '''
                '''
                print(i)
                # transfer image of pdf_file into array
                page_arr = np.asarray(page)
                # transfer into grayscale
                page_arr_gray = cv2.cvtColor(page_arr,cv2.COLOR_BGR2GRAY)
                # deskew the page
                page_deskew = deskew(page_arr_gray)
                # cal confidence value
                page_conf = get_conf(page_deskew)
                # extract string 
                pages_df = pages_df.append({'conf': page_conf,'text': pytesseract.image_to_string(page_deskew)}, ignore_index=True)
                print(pages_df)
                '''
            except:
                print("EXCEPTION")
                traceback.print_exc()
                break
                # if can't extract then give some notes into df
                #pages_df = pages_df.append({'conf': -1,'text': 'N/A'}, ignore_index=True)
                """
        output_stream = open(output_file, "wb")
        output.write(output_stream)
        output_stream.close()
        main_i=main_i+1
        
files=["D:\\DEV\\CANATHIST\\test_pdf_ocr_larissa\\Ann.Mus.Terv.in-8o.Zool.001-11-40-1.pdf"]
files_with_text=["D:\\DEV\\CANATHIST\\test_pdf_ocr_larissa\\Ann.Mus.Terv.in-8o.Zool.001-11-40-1_text.pdf"]
ocr_extract(files, files_with_text)