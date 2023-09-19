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

#SRC_FILE="irscnb_d1684_012e6ex_1_corps-de-texte-red_wrk-10-15.pdf"
SRC_FILE="Capart_1955_Mission_De-Brouwer.pdf"
POPPLER_PATH="C:\\DEV\\CANATHIST\\tiff_to_ocr_pdf\\POPPLER\\Release-23.08.0-0\\poppler-23.08.0\\Library\\bin"

#import matplotlib.pyplot as plt


list_height=[]

global_rows=[]

def get_contour_precedence(contour, cols):
    tolerance_factor = 10
    origin = cv2.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]


def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2)/2)
    y_mid = int((y1 + y2)/2)
    return (x_mid, y_mid)

def inpaint_text_keras(img_path, pipeline, tolerance_factor=2):
    # read image
    img = keras_ocr.tools.read(img_path)
    # generate (word, box) tuples 
    prediction_groups = pipeline.recognize([img])
    mask = np.zeros(img.shape[:2], dtype="uint8")
    for box in prediction_groups[0]:
        x0, y0 = box[1][0] 
        x1, y1 = box[1][1] 
        x2, y2 = box[1][2]
        x3, y3 = box[1][3] 
        x0=x0+tolerance_factor
        y0=y0+tolerance_factor
        x1=x1-tolerance_factor
        y1=y1+tolerance_factor
        x2=x2-tolerance_factor
        y2=y2-tolerance_factor
        x3=x3+tolerance_factor
        y3=y3-tolerance_factor
        
        
        x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
        x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)
        
        thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))
        if thickness<1:
            thickness=1
        
        cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255,    
        thickness)
    img = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)
                 
    return(img)

def inpaint_text_tesser(img_path, tolerance_factor=0):
    data = pytesseract.image_to_data(img_path, output_type=Output.DICT, config='digit')
    #print(data)
    n_boxes = len(data['level'])
    mask = np.zeros(img_path.shape[:2], dtype="uint8")
    
    for i in range(n_boxes):
        
        if len(data["text"][i])>0:
            if  not re.search('[a-zA-Z]', data["text"][i]) is None:
                
                
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                #cv2.rectangle(img_path, (x, y), (x + w, y + h), (0, 255, 0), 2)
                x0=x
                y0=y
                x1=x+w
                y1=y
                x2=x+w
                y2=y+h
                x3=x
                y3=y+h
                
                x0=x0+tolerance_factor
                y0=y0+tolerance_factor
                x1=x1-tolerance_factor
                y1=y1+tolerance_factor
                x2=x2-tolerance_factor
                y2=y2-tolerance_factor
                x3=x3+tolerance_factor
                y3=y3-tolerance_factor
                x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
                x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)
                
                thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))
                if thickness<1:
                   thickness=1 
                cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255,    
                thickness)
    img = cv2.inpaint(img_path, mask, 7, cv2.INPAINT_NS)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    img = cv2.filter2D(img, -1, kernel)
    #display_with_factor(img_path,0.5)
    #display_with_factor(img,0.5)
    img=inpaint_text_tesser_text(img,0)
    return (img)
    '''
     for text in data["text"]:
        if len(text)>0:
    '''   
    
def inpaint_text_tesser_text(img_path, tolerance_factor=0):
    data = pytesseract.image_to_data(img_path, output_type=Output.DICT, config='-c preserve_interword_spaces=1')
    #print(data)
    n_boxes = len(data['level'])
    mask = np.zeros(img_path.shape[:2], dtype="uint8")
    
    for i in range(n_boxes):
        
        if len(data["text"][i])>0:
            if  not re.search('[a-zA-Z]', data["text"][i]) is None:
                
                
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                #cv2.rectangle(img_path, (x, y), (x + w, y + h), (0, 255, 0), 2)
                x0=x
                y0=y
                x1=x+w
                y1=y
                x2=x+w
                y2=y+h
                x3=x
                y3=y+h
                
                x0=x0+tolerance_factor
                y0=y0+tolerance_factor
                x1=x1-tolerance_factor
                y1=y1+tolerance_factor
                x2=x2-tolerance_factor
                y2=y2-tolerance_factor
                x3=x3+tolerance_factor
                y3=y3-tolerance_factor
                x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
                x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)
                
                thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))
                if thickness<1:
                   thickness=1 
                cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255,    
                thickness)
    img = cv2.inpaint(img_path, mask, 7, cv2.INPAINT_NS)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    img = cv2.filter2D(img, -1, kernel)
    #display_with_factor(img_path,0.5)
    #display_with_factor(img,0.5)
    return (img)
    '''
     for text in data["text"]:
        if len(text)>0:
    '''   

def display_with_factor(p_image, p_factor, window="", blocking=True):    
    cpy = cv2.resize(p_image, (0,0), fx=p_factor, fy=p_factor)
    cv2.imshow(window,cpy)
    if blocking:
        cv2.waitKey(0)
    




    
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

def get_tesseract_overlap(contours, irect, tesseract_list, tresh=0.5):
    x,y,w,h = cv2.boundingRect(contours[irect])    
    
    i=0
    list_result=[]
    for text in tesseract_list['text']:
        if len(text.strip())>0 and text.strip()!="|":
            #print("test :"+text)
            #print(len(text))
            x2=tesseract_list['left'][i]
            y2=tesseract_list['top'][i]
            w2=tesseract_list['width'][i]
            h2=tesseract_list['height'][i]
            ref_area=w2*h2
            cmp_area=do_overlap(x, y, w, h, x2, y2, w2, h2)
            if cmp_area>0:
                ratio=cmp_area/ref_area
                if ratio>=tresh:
                    list_result.append(text)
        i=i+1
    return list_result

def translate_rect( contours, grid_idx, irect, step_x, step_y, limit_x, limit_y , list_r, depth=1):
    
    list_r.append(irect)
    x,y,w,h = cv2.boundingRect(contours[irect])
    #print(str(cv2.boundingRect(contours[irect])))
    if step_x>0:
        x=x+step_x
    elif step_y>0:
        y=y+step_y
        #print("offset y")
        #print(str([x,y,w,h]))
    if x<limit_x and y<limit_y:
        #cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 0) 
        #display_with_factor(img, 0.5)        
        current_overlap=0
        current_i=-1
        for i in grid_idx:
            if i!=irect and i not in list_r:
                x2,y2,w2,h2 = cv2.boundingRect(contours[i])
                area=do_overlap(x, y, w, h, x2, y2, w2, h2)
                if area>current_overlap:
                    #print("current_overlap="+str(area))
                    current_overlap=area
                    current_i=i
        if current_i>-1:
            #print("next_Rect="+str(current_i))
            x3,y3,w3,h3 = cv2.boundingRect(contours[current_i])
            #print(str(cv2.boundingRect(contours[current_i])))
            #cv2.rectangle(img, (x3,y3), (x3+w3,y3+h3), (0,255,0), 0)    
            #display_with_factor(img,0.5)
            #crop_img = img[y3:y3+h3, x3:x3+w3]
            #display_with_factor(crop_img, 1)
            translate_rect(contours, grid_idx, current_i, step_x, step_y, limit_x, limit_y, list_r, depth=depth+1)
             
    
def extract_grid(p_input_file, p_pipeline):
    
    global global_rows
    list_height=[]
    matrix_cell=[]
    #display_with_factor(p_input_file, 0.75,"main", True)
    gray0 = cv2.cvtColor(p_input_file, cv2.COLOR_BGR2GRAY)
    #grid_only=inpaint_text_tesser(gray0)
    grid_only=inpaint_text_keras(p_input_file, p_pipeline, 0)
    
    gray = cv2.cvtColor(grid_only, cv2.COLOR_BGR2GRAY)
    #gray=grid_only
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    #display_with_factor(blur, 0.5)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    #display_with_factor(thresh, 0.5)
    #Apply a morphological operation to close gaps in the lines original 30 30
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30,30))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find the contours in the binary image
    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)
    hierarchy=hierarchy[0]
    
    # Initialize a list to store the coordinates of the vertical lines
    vertical_lines = []
    cpy=p_input_file.copy()
    # Iterate through each contour and extract the coordinates of the bounding rectangle if it's a vertical line
    i=0
    #parents={}
    tree_key={}
    i=0
    for pos_hierarch in hierarchy:
        if hierarchy[pos_hierarch[3]][3]==-1:
            if pos_hierarch[3] not in tree_key:
                tree_key[pos_hierarch[3]]=[]
            tree_key[pos_hierarch[3]].append(i)
        i=i+1
    '''
    for pos_hierarch in hierarchy:
        if pos_hierarch[3]==-1:
            parents[i]=tree_key[i]
        i=i+1
    '''
    #print(tree_key)
    main_grid=max(tree_key, key=lambda x: len(tree_key[x]))
    #print("main grid="+str(main_grid))
    #parent=contours[main_grid]
    grid=tree_key[main_grid]
    #print(grid)
    '''
    x,y,w,h = cv2.boundingRect(parent)
    cv2.rectangle(cpy, (x,y), (x+w,y+h), (0,255,0), 0)
    '''
    #display_with_factor(cpy, 0.5)
    """
    left_elems = min(grid, key=lambda x: cv2.boundingRect(contours[x])[0])
    print(left_elems)
    """
    for icontour in grid:
        x,y,w,h = cv2.boundingRect(contours[icontour])
        print(str((x,y,w,h)))
        cv2.rectangle(cpy, (x,y), (x+w,y+h), (255,0,0), 0)
        cv2.putText(cpy, str(icontour), (x,y), cv2.FONT_HERSHEY_SIMPLEX,1, 255)
    
    i=0
    min_x=0
    left=[]
    for icontour in grid:
        #print("icontour="+str(icontour))
        cx,cy,cw,ch= cv2.boundingRect(contours[icontour])
        #print(str(cv2.boundingRect(contours[icontour])))
        if i==0:            
            min_x=cx
            left.append(icontour)
            #print("min_x (1)="+str(min_x))
        elif cx<min_x:
            left=[]
            left.append(icontour)
            min_x=cx
            #print("min_x (2) ="+str(min_x))
        elif cx==min_x:
            left.append(icontour)
            #print("min_x (3)="+str(min_x))
        i=i+1
        #i=i+1
    print("left="+str(left))
    #display_with_factor(cpy, 0.5)
    i=0
    min_y=0
    top_left=[]
    for idx in left:
        cx,cy,cw,ch = cv2.boundingRect(contours[idx])
        if i==0:
            min_y=cy
            top_left.append(idx)
        elif cy<min_y:
            top_left=[]
            min_y=cy
            top_left.append(idx)
            #print("min_y="+str(min_y))
        elif cy==min_y:
            top_left.append(idx)
            #print("min_y="+str(min_y))
        i=i+1
    print("top_left="+str(top_left))    
    if len(top_left)>0:        
        #x,y,w,h = cv2.boundingRect(contours[top_left[0]])
        #cv2.rectangle(cpy, (x,y), (x+w,y+h), (255,0,0), 0)    
        #display_with_factor(cpy, 0.5)
        
        translate_rect( contours, grid, top_left[0],  0, 10, gray0.shape[1], gray0.shape[0],list_height)
        print("list_height="+str(list_height))
        i=0
        for left in list_height:
            #print("ROW "+str(i))
            right=[]
            
            translate_rect( contours, grid, left,  10,0, gray0.shape[1], gray0.shape[0],right)
            print(right)
            matrix_cell.append(right)
            i=i+1
    #print(tree_key[main_grid])
    #print(matrix_cell)
    longuest=max(len(x) for x in matrix_cell)
    #print(longuest)
    data = pytesseract.image_to_data(gray0, output_type='dict', config='-c preserve_interword_spaces=1')
    #print(str(data))
    keysList = list(data.keys())
    
    #print(keysList)
    for row in matrix_cell:
        #print(row)
        row_text=[]
        for icell in row:
            '''
            current_cell=contours[icell]
            x,y,w,h = cv2.boundingRect(current_cell)
            cv2.rectangle(cpy, (x,y), (x+w,y+h), (0,255,0), 0)
            crop_img = gray0[y:y+h, x:x+w]
            #str_ocr = pytesseract.image_to_string(crop_img,  config=' -c tessedit_char_whitelist=0123456789')
            #print(str_ocr)
            display_with_factor(crop_img, 1)
            row_text.append(str_ocr)
            '''
            current_cell=contours[icell]
            x,y,w,h = cv2.boundingRect(current_cell)
            crop_img = gray0[y:y+h, x:x+w]
            list_word=get_tesseract_overlap(contours, icell, data, tresh=0.5)
            #print(list_word)
            row_text.append("\r\n".join(list_word).strip())
            #display_with_factor(crop_img, 1)
        '''
        if len(row)<longuest:
            print('smaller')
            print(len(row))
         '''
        #print(row_text)
        global_rows.append(row_text)
    return 
    
    
    
def start_ocr(p_input_file,  p_tesseract_path,  p_poppler_mode, p_poppler_path, page_begin, page_end, p_pipeline):
    global global_rows
    pytesseract.pytesseract.tesseract_cmd =   p_tesseract_path 
    print("loading...")
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
                extract_grid(image_ori, p_pipeline)
            
        except Exception as e2:
            traceback.print_exception(*sys.exc_info())
    print("DISPLAY")
    for row in global_rows:
        print(row)

print(cv2.__version__)
pipeline = None
pipeline = keras_ocr.pipeline.Pipeline()
start_ocr(SRC_FILE, "C:\\Program Files\\Tesseract-OCR\\tesseract.exe", False, POPPLER_PATH, 0, 0, pipeline)