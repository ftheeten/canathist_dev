import traceback
import sys
import numpy as np
import cv2
from pdf2image import convert_from_path


SRC_FILE="C:\\DEV\CANATHIST\\tiff_to_ocr_pdf\\irscnb_d1684_012e6ex_1_corps-de-texte-red_wrk.pdf"
POPPLER_PATH="C:\\DEV\\CANATHIST\\tiff_to_ocr_pdf\\POPPLER\\Release-23.08.0-0\\poppler-23.08.0\\Library\\bin"

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
def extract_grid(p_input_file):
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
    gray = cv2.cvtColor(p_input_file, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    #Apply a morphological operation to close gaps in the lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30,30))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find the contours in the binary image
    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store the coordinates of the vertical lines
    vertical_lines = []
    cpy=p_input_file.copy()
    # Iterate through each contour and extract the coordinates of the bounding rectangle if it's a vertical line
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        #if w < h/5:  # adjust this value based on the width of your lines
            # Append the coordinates of the vertical line to the list
        vertical_lines.append((x,y,x+w,y+h))
            
            # Draw a rectangle around the vertical line
        cv2.rectangle(cpy, (x,y), (x+w,y+h), (0,255,0), 2)


    # Print the coordinates of the vertical lines
    #print(vertical_lines)
    display_with_factor(cpy, 0.33)
def start_ocr(p_input_file, p_poppler_mode, p_poppler_path):
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
            image_ori = np.asarray(page)
            display_with_factor(image_ori, 0.33)            
            extract_grid(image_ori)
            
        except Exception as e2:
            traceback.print_exception(*sys.exc_info())



start_ocr(SRC_FILE, True, POPPLER_PATH)