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
import matplotlib.pyplot as plt
from scipy import ndimage
from itertools import groupby
from operator import itemgetter

global_rows=[]
SRC_FILE="irscnb_d1684_012e6ex_1_corps-de-texte-red_wrk-10-15.pdf"
#SRC_FILE="Capart_1955_Mission_De-Brouwer.pdf"
#SRC_FILE="CIA-RDP01-00707R000100130010-3-Republic-of-the-Congo-9-15.pdf"
#SRC_FILE="20230914164804.pdf"
POPPLER_PATH="C:\\DEV\\CANATHIST\\tiff_to_ocr_pdf\\POPPLER\\Release-23.08.0-0\\poppler-23.08.0\\Library\\bin"


def display_with_factor(p_image, p_factor=0.5, window="", blocking=True):    
    cpy = cv2.resize(p_image, (0,0), fx=p_factor, fy=p_factor)
    cv2.imshow(window,cpy)
    if blocking:
        cv2.waitKey(0)

def do_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type='dict', config='-c preserve_interword_spaces=1')
    
    '''
    i=0
    for text in data['text']:
        if len(text.strip())>0 and text.strip()!="|":
            #print("test :"+text)
            #print(text)
            x=data['left'][i]
            y=data['top'][i]
            w=data['width'][i]
            h=data['height'][i]
            
            cv2.putText(img, text, (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255,0,0))
        i=i+1
    cv2.imwrite("debug_nima_tesseract_rmca.jpg",img)
    display_with_factor(img,0.7)
    '''
    return data

def do_overlap(r1_x, r1_y, r1_w, r1_h,r2_x, r2_y, r2_w, r2_h ):
    r1_l= r1_x
    r1_t= r1_y
    r1_r= r1_x + r1_w
    r1_b= r1_y + r1_h
    
    r2_l= r2_x
    r2_t= r2_y
    r2_r= r2_x + r2_w
    r2_b= r2_y + r2_h
    
    
    dx=min( r1_r, r2_r)-max(r1_l, r2_l)
    dy=min( r1_b , r2_b)-max(r1_t, r2_t)
    if (dx>=0) and (dy>=0):
        return dx*dy
    return 0

def balayage_y(image, tesseract_data):
    x1=0
    y1=0
    limit_x=image.shape[1]
    limit_y=image.shape[0]
    no_overlaps=[]
    for y1 in range(0, limit_y):
        print(y1)
        
        list_overlap=[]
        i =0
        print(str((0,y1)))
        
   
        for text in tesseract_data['text']:
            if len(text.strip())>0 and text.strip()!="|":
                x=tesseract_data['left'][i]
                y=tesseract_data['top'][i]
                w=tesseract_data['width'][i]
                h=tesseract_data['height'][i]
                overlap=do_overlap(x, y, w, h, 0, y1, limit_x, 1)
                if overlap>0:
                    list_overlap.append(i)
                    #cv2.line(image, (0, y1), (limit_x, y1), (0, 0, 255), 3, cv2.LINE_AA)
                    #display_with_factor(image,0.7)
            i=i+1
        if len(list_overlap)==0:
            no_overlaps.append(y1)
    print(no_overlaps)
    y_lines=[]
    for k, g in groupby(enumerate(no_overlaps), lambda ix : ix[0] - ix[1]):
        tmp=list(map(itemgetter(1), g))
        if len(tmp)>0:
            y_lines.append(tmp[-1])
    print(y_lines)
    return y_lines

def balayage_x(image, tesseract_data):
    x1=0
    y1=0
    limit_x=image.shape[1]
    limit_y=image.shape[0]
    no_overlaps=[]
    for x1 in range(0, limit_x):
        print(x1)
        
        list_overlap=[]
        i =0
        print(str((x1,0)))
        
   
        for text in tesseract_data['text']:
            if len(text.strip())>0 and text.strip()!="|":
                x=tesseract_data['left'][i]
                y=tesseract_data['top'][i]
                w=tesseract_data['width'][i]
                h=tesseract_data['height'][i]
                overlap=do_overlap(x, y, w, h, x1, 0, 1, limit_y)
                if overlap>0:
                    list_overlap.append(i)
                    #cv2.line(image, (0, y1), (limit_x, y1), (0, 0, 255), 3, cv2.LINE_AA)
                    #display_with_factor(image,0.7)
            i=i+1
        if len(list_overlap)==0:
            no_overlaps.append(x1)
    #print(no_overlaps)
    x_lines=[]
    for k, g in groupby(enumerate(no_overlaps), lambda ix : ix[0] - ix[1]):
        tmp=list(map(itemgetter(1), g))
        if len(tmp)>0:
            x_lines.append(tmp[-1])
    #print(x_lines)
    return x_lines    
    
def rotate_image(image, angle):
    print(angle)
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    #display_with_factor(result,0.7)
   
    return result
    


def detect_rotation(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    minLineLength=200
    lines = cv2.HoughLinesP(image=edges,rho=1,theta=np.pi/180, threshold=100,lines=np.array([]), minLineLength=minLineLength,maxLineGap=80)
    a,b,c = lines.shape
    acc=[]
    for i in range(a):
        x1=lines[i][0][0]
        y1=lines[i][0][1]
        x2=lines[i][0][2]
        y2=lines[i][0][3]
        #cv2.line(gray, (x1, y1), (x2, y2), (0, 0, 255), 3, cv2.LINE_AA)
        
        if x2!=x1:
            angle = float(math.atan((y2-y1)/(x2-x1))*180/math.pi)
            if angle<15 and angle>-15:
                acc.append(angle)
    if len(acc)>0:
        avg_angle=float(sum(acc)/len(acc))
    else:
        avg_angle=0
    #print("AVG_ANGLE="+str(avg_angle))
   
    diff=avg_angle
    
    #display_with_factor(rotate_image(img,diff ))
    if diff!=0:
        return rotate_image(img,diff )
    else:
        return img
  

   
    
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
    list_img=[]
    for (i,page) in enumerate(pdf_file) :            
        try:
            print("--------------------------------------------------------------------------")
            print("PAGE "+str(i))
            if i>=page_begin and i <=page_end:
                
                image_ori = np.asarray(page)
                #display_with_factor(image_ori,0.7)
                image_ori=detect_rotation(image_ori)
                #display_with_factor(image_ori, 0.33)            
                #tresh=remove_grid(image_ori)
                #main_grid=get_main_grid(image_ori, pipeline)
                #do_ocr(tresh, main_grid)
                #list_img.append(image_ori)
                dict_t=do_ocr(image_ori)
                y_lines=balayage_y(image_ori, dict_t)
                x_lines=balayage_x(image_ori, dict_t)
                limit_x=image_ori.shape[1]
                limit_y=image_ori.shape[0]
                cpy=image_ori.copy()
                for y in y_lines:
                    cv2.line(cpy, (0, y), (limit_x, y), (0, 0, 255), 3, cv2.LINE_AA)
                    
                for x in x_lines:
                    cv2.line(cpy, (x, 0), (x, limit_y), (0, 0, 255), 3, cv2.LINE_AA)
                display_with_factor(cpy, 0.7)  
        except Exception as e2:
            traceback.print_exception(*sys.exc_info())
    print("DISPLAY")
    
    #images = [ keras_ocr.tools.read(img) for img in list_img]
    
print(cv2.__version__)

start_ocr(SRC_FILE, 0, 5,  "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")