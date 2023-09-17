import traceback
import sys
import numpy as np
import cv2
from pdf2image import convert_from_path
import pytesseract
import math

SRC_FILE="C:\\DEV\CANATHIST\\tiff_to_ocr_pdf\\irscnb_d1684_012e6ex_1_corps-de-texte-red_wrk-10-15.pdf"
POPPLER_PATH="C:\\DEV\\CANATHIST\\tiff_to_ocr_pdf\\POPPLER\\Release-23.08.0-0\\poppler-23.08.0\\Library\\bin"

#import matplotlib.pyplot as plt
import keras_ocr

def get_contour_precedence(contour, cols):
    tolerance_factor = 10
    origin = cv2.boundingRect(contour)
    return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]


def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2)/2)
    y_mid = int((y1 + y2)/2)
    return (x_mid, y_mid)

def inpaint_text(img_path, pipeline):
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
        
        x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
        x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)
        
        thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))
        
        cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255,    
        thickness)
        img = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)
                 
    return(img)

def display_with_factor(p_image, p_factor):    
    cpy = cv2.resize(p_image, (0,0), fx=p_factor, fy=p_factor)
    cv2.imshow('image',cpy)
    cv2.waitKey(0)
    

'''    
def extract_grid2(p_input_file):
    cpy=p_input_file.copy()
    gray=cv2.cvtColor(p_input_file,cv2.COLOR_BGR2GRAY)
    ret2,th2 = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    ###applying morphological operations to dilate the image
    kernel=np.ones((3,3),np.uint8)
    dilated=cv2.dilate(th2,kernel,iterations=3)

    ### finding contours, can use connectedcomponents aswell
    _,contours = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ### converting to bounding boxes from polygon
    contours=[cv2.boundingRect(cnt) for cnt in contours]
    ### drawing rectangle for each contour for visualising
    for cnt in contours:
        x,y,w,h=cnt
        cv2.rectangle(cpy,(x,y),(x+w,y+h),(0,255,0),2)
    display_with_factor(  cpy, 0.33)
'''   

def do_ocr(p_image):
    data = pytesseract.image_to_string(p_image, output_type='dict', config='-c preserve_interword_spaces=1')
    j=0
    '''
    for text in data["text"]:
        if len(text)>0:
            print(text)
            #font_size=data['height'][j]/ratio_height*FONT_TO_PIXEL_RATIO
            #can.setFont("Courier", font_size)
            #can.drawString( (data['left'][j])/ratio_width, math.floor(pdf_height)-(data['top'][j]/ratio_height)-(data['height'][j]/ratio_height),text)
        j=j+1  
    '''
    return data
def extract_grid(p_input_file, p_pipeline):
    """
    gray = cv2.cvtColor(p_input_file, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,1))
    horizontal_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,25))
    vertical_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    # Combine masks and remove lines
   
    display_with_factor( thresh, 0.33)
    display_with_factor(  horizontal_mask, 0.33)
    display_with_factor( vertical_mask, 0.33)
    display_with_factor(  table_mask, 0.33)
   
    cv2.waitKey()    
    """
    grid_only=inpaint_text(p_input_file, p_pipeline)
    display_with_factor(grid_only, 0.75)
    gray = cv2.cvtColor(grid_only, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    #Apply a morphological operation to close gaps in the lines original 30 30
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30,30))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find the contours in the binary image
    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)
    hierarchy=hierarchy[0]
    print(hierarchy)
    do_ocr(gray)
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
    print(tree_key)
    main_grid=max(tree_key, key=lambda x: len(tree_key[x]))
    print(tree_key[main_grid])
    list_contour=[]
    for i in tree_key[main_grid]:
        contour=contours[i]
        list_contour.append(contour)
        x,y,w,h = cv2.boundingRect(contour)
        cv2.rectangle(cpy, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(cpy, str(i)+ ":"+str(hierarchy[i][2]), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 255)
        
    list_contour.sort(key=lambda x:get_contour_precedence(x, cpy.shape[1]))

    # For debugging purposes.
    last_x=0    
    current_x=0
    current_row=[]
    current_grid=[]
    current_column=0
    
    for i in range(0, len(list_contour)):
        cv2.putText(cpy, str(i), cv2.boundingRect(list_contour[i])[:2], cv2.FONT_HERSHEY_COMPLEX, 1, [125])
        current_x,y,w,h = cv2.boundingRect(list_contour[i])
        if current_x>last_x and i<len(list_contour)-1:
            current_row.append(list_contour[i])
            last_x=current_x
        else:
            print("END ROW "+str(i))
            current_grid.append(current_row.copy())
            last_x=0
            current_row=[]
            current_row.append(list_contour[i])
            
    for i in range(0, len(current_grid)):
        row=current_grid[i]
        for j in range(0, len(row)):
            current_rect=row[j]
            x,y,w,h = cv2.boundingRect(list_contour[j])
            crop_img = cpy[y:y+h, x:x+w]
            display_with_factor(crop_img, 1)
            str_ocr = pytesseract.image_to_string(crop_img,  config='-c preserve_interword_spaces=1')
            print("text for "+str(i)+" "+str(j)+" "+str_ocr)
    # Print the coordinates of the vertical lines
    #print(vertical_lines)
    display_with_factor(cpy, 0.25)
    
def start_ocr(p_input_file,  p_tesseract_path,  p_poppler_mode, p_poppler_path, page_begin, page_end, p_pipeline):
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
            print(i)
            if i+1>=page_begin and i+1 <=page_end:
                image_ori = np.asarray(page)
                display_with_factor(image_ori, 0.33)            
                extract_grid(image_ori, p_pipeline)
            
        except Exception as e2:
            traceback.print_exception(*sys.exc_info())


print(cv2.__version__)
pipeline = keras_ocr.pipeline.Pipeline()
start_ocr(SRC_FILE, "C:\\Program Files\\Tesseract-OCR\\tesseract.exe", True, POPPLER_PATH, 1.1, 5, pipeline)