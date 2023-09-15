from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel, QCheckBox, QMessageBox, QComboBox, QSizePolicy
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
layout=None
console=None
filenames=[]
folders=[]
folders_output=[]
lab_tesseract=None
lab_height=None
lab_opacity=None




output_pdf_file=None
input_height=None
input_tesseract=None
chkJPEG=None
input_ratioJPEG=None
input_opacity=None
combobox_mode= None
but_change_tesseract= None
but_tif=None

CONFIG_FILE="config.cfg"
TESSERACT_PATH=""
USER_TESSERACT_PATH=""

HEIGHT_IMAGE_CM=""
USER_HEIGHT_IMAGE_CM=""
USER_HEIGHT_IMAGE_PX=""
PIXEL_PER_CM=""
JPEG_RATIO=""
USER_JPEG_RATIO=""
FONT_TO_PIXEL_RATIO=0.75

POPPLER_MODE=False

POPPLER_PATH=None
USER_POPPLER_PATH=None

chkAdmin=None
MODE_ADMIN=False
MODE_FOLDER=False


chkPoppler=None
labPoppler=None
but_change_poppler=None
inputPoppler=None

HSV_H_MIN=None
HSV_S_MIN=None
HSV_V_MIN=None
HSV_H_MAX=None
HSV_S_MAX=None
HSV_V_MAX=None

USR_HSV_H_MIN=None
USR_HSV_S_MIN=None
USR_HSV_V_MIN=None
USR_HSV_H_MAX=None
USR_HSV_S_MAX=None
USR_HSV_V_MAX=None

HSV_MODE=True
chk_hsv=None
label_hsv_h_min=None
label_hsv_s_min=None
label_hsv_v_min=None
label_hsv_h_max=None
label_hsv_s_max=None
label_hsv_v_max=None


input_hsv_h_min=None
input_hsv_s_min=None
input_hsv_v_min=None
input_hsv_h_max=None
input_hsv_s_max=None
input_hsv_v_max=None


OPACITY=0.0
USER_OPACITY=0.0


class CustomFileDialog(QFileDialog):
    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        #self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QtGui.QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QtGui.QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                files.append(os.path.join(str(self.directory().absolutePath()),str(i.data().toString())))
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles


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
    

 

    
def apply_hsv_correction(p_img,p_lower_white, p_upper_white):
    hsv = cv2.cvtColor(p_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, p_lower_white, p_upper_white)
    mask=cv2.bitwise_not(mask)
    result = cv2.bitwise_and(p_img, p_img, mask=mask)
    black_pixels = np.where(
            (result[:, :, 0] == 0) & 
            (result[:, :, 1] == 0) & 
            (result[:, :, 2] == 0)
    )
    result[black_pixels] = [255, 255, 255]
    return result

def ocr_logic(p_img):
    page_arr_gray = cv2.cvtColor(p_img,cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(page_arr_gray, output_type='dict', config='-c preserve_interword_spaces=1')
    return data

    
def generate_pdf(p_input_files, p_output_file, opacity, convert_to_jpeg,  correct_background=False, hsv_background_filter=[] ):
    global USER_JPEG_RATIO
    global input_ratioJPEG
    global FONT_TO_PIXEL_RATIO
    global window
    try:
        print("generating  temporary PDF")
        print("loading file...")
        display_time()
        color_image = Color( 0, 0, 0, alpha=1.0)
        color_transparent = Color( 0, 0, 0, alpha=opacity)
        '''
        can = canvas.Canvas(p_output_file)
        can.setFillColor(color_transparent)
        '''
        can = canvas.Canvas(p_output_file)
        
        p_input_files.sort()
        print("nb pages="+str(len(p_input_files)))
        for i, image_path in enumerate(p_input_files):
            if convert_to_jpeg:
                USER_JPEG_RATIO=input_ratioJPEG.text()
                go_jpeg=False
                int_USER_JPEG_RATIO=0
                try:
                    int_USER_JPEG_RATIO=int(USER_JPEG_RATIO)
                    go_jpeg=True
                except Exception:
                    QMessageBox.about(window, 'Error','JPEG Ratio can only be a number')
                    return
                if go_jpeg:
                    if int_USER_JPEG_RATIO<0 or int_USER_JPEG_RATIO>100:
                        QMessageBox.about(window, 'Error','JPEG must be between 0 and 100')
                        go_jpeg=False
                        return
                if go_jpeg:
                    image_ori = cv2.imread(image_path)
                    data=ocr_logic(image_ori)
                    if correct_background:                        
                        p_l_filter=(hsv_background_filter[0],hsv_background_filter[1],hsv_background_filter[2])
                        p_h_filter=(hsv_background_filter[3],hsv_background_filter[4],hsv_background_filter[5])
                        image_ori=apply_hsv_correction(image_ori, p_l_filter, p_h_filter )
                    is_success, buffer = cv2.imencode(".jpg", image_ori, [int(cv2.IMWRITE_JPEG_QUALITY), int_USER_JPEG_RATIO])
                    pdf_tmp_buffer=ImageReader(io.BytesIO(buffer.tobytes()))     
                    image= cv2.imdecode(buffer,cv2.IMREAD_COLOR)
                    
                    size_ratio=resize_image_target_height( image)                  
                    can.setFillColor(color_image)
                    can.setPageSize((image.shape[1]*size_ratio,image.shape[0]*size_ratio))                        
                    new_width=image.shape[1]*size_ratio
                    new_height=image.shape[0]*size_ratio                 
                    can.drawImage(pdf_tmp_buffer, 0, 0, width=new_width, height=new_height)                   
                    j=0
                    can.setFillColor(color_transparent)
                    for text in data["text"]:
                        if len(text)>0:
                            font_size=data['height'][j]*size_ratio*FONT_TO_PIXEL_RATIO                            
                            str_y=(data['left'][j])*size_ratio
                            str_x=math.floor(new_height)-(data['top'][j]*size_ratio)-(data['height'][j]*size_ratio)
                            can.setFont("Courier", font_size)                            
                            can.drawString( str_y, str_x ,text)                            
                        j=j+1                    
                    can.showPage()
                    if (i+1)%10==0:
                        print("page (intermediate PDF) "+str(i+1)+"/"+str(len(p_input_files)))
                        display_time()
            else:                
                image_ori = cv2.imread(image_path)
                data=ocr_logic(image_ori)
                if correct_background:                        
                    p_l_filter=(hsv_background_filter[0],hsv_background_filter[1],hsv_background_filter[2])
                    p_h_filter=(hsv_background_filter[3],hsv_background_filter[4],hsv_background_filter[5])
                    image_ori=apply_hsv_correction(image_ori, p_l_filter, p_h_filter )
                size_ratio=resize_image_target_height( image_ori)                  
                can.setFillColor(color_image)
                can.setPageSize((image_ori.shape[1]*size_ratio,image_ori.shape[0]*size_ratio))                        
                new_width=image_ori.shape[1]*size_ratio
                new_height=image_ori.shape[0]*size_ratio                 
                can.drawImage(image_path, 0, 0, width=new_width, height=new_height)                   
                j=0
                can.setFillColor(color_transparent)
                for text in data["text"]:
                    if len(text)>0:
                        font_size=data['height'][j]*size_ratio*FONT_TO_PIXEL_RATIO                            
                        str_y=(data['left'][j])*size_ratio
                        str_x=math.floor(new_height)-(data['top'][j]*size_ratio)-(data['height'][j]*size_ratio)
                        can.setFont("Courier", font_size)                            
                        can.drawString( str_y, str_x ,text)                            
                    j=j+1                    
                can.showPage()
                if (i+1)%10==0:
                    print("page (intermediate PDF) "+str(i+1)+"/"+str(len(p_input_files)))
                    display_time()          
        can.save()
        #can=None
        #can=None
        print("Done")
        display_time()    
    except:    
        traceback.print_exception(*sys.exc_info())
    

    


def choose_tifs(x):
    global window
    global filenames
    global folders
    global combobox_mode
    global MODE_FOLDER
    global console
    tmp_text=console.text()
    
    print(combobox_mode.currentIndex())
    if not MODE_FOLDER:
        
        file_name = QFileDialog()
        filter = "TIFF (*.TIF);;tiff (*.tif);;TIFF (*.TIFF);;tiff (*.tiff);;JPG (*.jpg);;JPG (*.JPG);;PNG (*.PNG);;PNG (*.png)"
        filenames, _ = file_name.getOpenFileNames(window, "Open files", "", filter)
        console.setText(tmp_text+"\nFILES\n"+"\n".join(filenames))
    else:
        console.setText(tmp_text+"\nFOLDER")
        file= QFileDialog.getExistingDirectory(window, "Choose folder to add")
        if len(file)>0:
            folders.append(file)
        console.setText(tmp_text+"\nFILES\n"+"\n".join(folders))
    
def choose_output():
    global window
    global output_pdf_file
    global console
    global filenames
    global folders
    global folders_output
    global MODE_FOLDER
    
    if not MODE_FOLDER:
        folder_object = QFileDialog()
        if len(filenames)>0:
            output_pdf_file =folder_object.getSaveFileName(window, dir=os.path.dirname(filenames[0])+".pdf",  caption='Select a data file', filter='PDF File (*.pdf)')[0]
        else:
            output_pdf_file =folder_object.getSaveFileName(window, caption='Select a data file', filter='PDF File (*.pdf)')[0]
        console.setText(console.text()+"\r\nOutput file: "+output_pdf_file)
    else:
        folders_output=[]
        folders = list(folders)
        for pdf_folder in folders:
            folder_object = QFileDialog()
            QMessageBox.about(window, 'Select output','Select output PDF for '+str(pdf_folder))
            output_pdf_file =folder_object.getSaveFileName(window, dir=pdf_folder+".pdf",  caption='Select a data file', filter='PDF File (*.pdf)')[0]
            
            if len(output_pdf_file)>0:
                folders_output.append(output_pdf_file)
            
def launch_ocr():
    global window
    global filenames
    global folders
    global folders_output
    global output_pdf_file
    global console
    global input_height
    global input_tesseract
    global input_opacity
    global chkJPEG
    global USER_HEIGHT_IMAGE_CM
    global USER_HEIGHT_IMAGE_PX
    global PIXEL_PER_CM
    global USER_TESSERACT_PATH
    global JPEG_RATIO
    global USER_JPEG_RATIO
    
    global USR_HSV_H_MIN
    global USR_HSV_S_MIN
    global USR_HSV_V_MIN
    global USR_HSV_H_MAX
    global USR_HSV_S_MAX
    global USR_HSV_V_MAX
    
    global input_hsv_h_min
    global input_hsv_s_min
    global input_hsv_v_min
    global input_hsv_h_max
    global input_hsv_s_max
    global input_hsv_v_max


    global MODE_FOLDER
    global HSV_MODE
    USER_HEIGHT_IMAGE_CM=float(input_height.text())
    USER_HEIGHT_IMAGE_PX=USER_HEIGHT_IMAGE_CM*float(PIXEL_PER_CM)
    
    

            
    USER_OPACITY=float(OPACITY)
    
    
    try:
        USER_OPACITY=float(input_opacity.text())
    except Exception:
        QMessageBox.about(window, 'Error','Opacity can only be a number')
        return
        
    if HSV_MODE:
        USR_HSV_H_MIN=int(input_hsv_h_min.text())
        USR_HSV_S_MIN=int(input_hsv_s_min.text())
        USR_HSV_V_MIN=int(input_hsv_v_min.text())
        USR_HSV_H_MAX=int(input_hsv_h_max.text())
        USR_HSV_S_MAX=int(input_hsv_s_max.text())
        USR_HSV_V_MAX=int(input_hsv_v_max.text())
        hsv_filter=[USR_HSV_H_MIN, USR_HSV_S_MIN, USR_HSV_V_MIN, USR_HSV_H_MAX, USR_HSV_S_MAX, USR_HSV_V_MAX]
    else:
        hsv_filter=[]
        
    #QMessageBox.about(window, 'OPACITY',str(USER_OPACITY))
    if not MODE_FOLDER:
        if output_pdf_file is None or filenames is None:
            console.setText(console.text()+"\r\nPDF files and/or Output folder not set")
            QMessageBox.about(window, 'Error','PDF files and/or Output folder not set')
            print("PDF files and/or Output folder not set")
        else:
            i=0           
            #print("user height "+str(USER_HEIGHT_IMAGE_CM)+"cm")
            #print("user height "+str(USER_HEIGHT_IMAGE_PX)+"pixels")
            temp=output_pdf_file
            generate_pdf(filenames, temp, USER_OPACITY, chkJPEG.isChecked(), HSV_MODE, hsv_filter)
            #ocr_extract(temp, USER_OPACITY)        

            print("DONE FOR "+output_pdf_file)
            display_time()
    else:
        if len(folders)==0 or len(folders_output)==0 :
            console.setText(console.text()+"\r\nPDF files and/or Output folder not set")
            QMessageBox.about(window, 'Error','PDF files and/or Output folder not set')
            print("PDF files and/or Output folder not set")
        elif len(folders)==len(folders_output):
            i=0
            for src_folder in folders:
                output_pdf_file=folders_output[i]
                filenames = [src_folder+"/"+f for f in os.listdir(src_folder) if f.lower().endswith('.tif') or  f.lower().endswith('.tiff')]
                
                print("PROCESSING "+str(src_folder)+"\tfolder "+str(i+1)+"/"+str(len(folders)))
                
                temp=output_pdf_file
                print(filenames)
                generate_pdf(filenames, temp,USER_OPACITY, chkJPEG.isChecked(), HSV_MODE, hsv_filter)
                #ocr_extract(temp, USER_OPACITY)
                print("DONE FOR "+output_pdf_file)
                display_time()                
                i=i+1
            folders=[]
        else:
            QMessageBox.about(window, 'Error','Different length for folder input and output files')
        
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
        
def choose_poppler():
    global window
    global USER_POPPLER_PATH
    global inputPoppler
    USER_POPPLER_PATH= QFileDialog.getExistingDirectory(window, "Choose Poppler folder")
    print(USER_POPPLER_PATH)
    if os.path.isdir(USER_POPPLER_PATH):       
        print("POPPLER ON "+ USER_POPPLER_PATH)
        inputPoppler.setText(USER_POPPLER_PATH)        
    else:
        print("POPPLER NOT FOUND - SET IT MANUALLY !!!!")
        
def enable_jpeg_conversion():
    global chkJPEG
    global input_ratioJPEG
    if chkJPEG.isChecked():
        input_ratioJPEG.setReadOnly(False)
        input_ratioJPEG.setDisabled(False)
    else:
        input_ratioJPEG.setReadOnly(True)
        input_ratioJPEG.setDisabled(True)
        
def hide_hsv_ctrl(flag):
    global label_hsv_h_min
    global input_hsv_h_min
    global label_hsv_s_min
    global input_hsv_s_min
    global label_hsv_v_min
    global input_hsv_v_min
    global label_hsv_h_max
    global input_hsv_h_max
    global label_hsv_s_max
    global input_hsv_s_max
    global label_hsv_v_max
    global input_hsv_v_max
    
    
    label_hsv_h_min.setVisible(flag)
    input_hsv_h_min.setVisible(flag)
    label_hsv_s_min.setVisible(flag)
    input_hsv_s_min.setVisible(flag)
    label_hsv_v_min.setVisible(flag)
    input_hsv_v_min.setVisible(flag)
        
    label_hsv_h_max.setVisible(flag)
    input_hsv_h_max.setVisible(flag)
    label_hsv_s_max.setVisible(flag)
    input_hsv_s_max.setVisible(flag)
    label_hsv_v_max.setVisible(flag)
    input_hsv_v_max.setVisible(flag)
    window.setFixedSize(window.sizeHint())
    window.setMinimumWidth(700)
        
def enable_background_normalization():
    global chk_hsv
    global HSV_MODE
    if chk_hsv.isChecked():
        HSV_MODE=True
    else:
        HSV_MODE=False
    hide_hsv_ctrl(HSV_MODE)
    
def enable_poppler():
    global chkPoppler
    global POPPLER_MODE
    if chkPoppler.isChecked():
        POPPLER_MODE=True
    else:
        POPPLER_MODE=False
        
def tiff_mode_changed(index):
    global MODE_FOLDER
    global folders
    global filenames
    filenames=[]
    folders=[]
    if index==0:
        but_tif.setText("Choose source Tifs")
        MODE_FOLDER=False
    elif index==1:
        but_tif.setText("Add folder")
        MODE_FOLDER=True
    enable_background_normalization(MODE_FOLDER)
    
def switch_admin_mode(mode):
    global MODE_ADMIN
    global MODE_FOLDER
    global window
    global lab_tesseract
    global input_tesseract
    global lab_ratioJPEG
    global lab_height
    global lab_opacity
    global input_height
    global input_ratioJPEG
    global input_opacity
    global but_change_tesseract
    global chkPoppler
    global inputPoppler
    global butPoppler
    global labPoppler
    global but_change_poppler
    
    global SIZE_W
    global ADMIN_SIZE_W
    MODE_ADMIN=mode
    
   
    lab_tesseract.setVisible(MODE_ADMIN)
    input_tesseract.setVisible(MODE_ADMIN)
    lab_ratioJPEG.setVisible(MODE_ADMIN)
    lab_height.setVisible(MODE_ADMIN)
    lab_opacity.setVisible(MODE_ADMIN)
    input_height.setVisible(MODE_ADMIN)
    input_ratioJPEG.setVisible(MODE_ADMIN)
    input_opacity.setVisible(MODE_ADMIN)
    but_change_tesseract.setVisible(MODE_ADMIN)
    chkPoppler.setVisible(MODE_ADMIN)
    inputPoppler.setVisible(MODE_ADMIN)
    labPoppler.setVisible(MODE_ADMIN)
    but_change_poppler.setVisible(MODE_ADMIN)
    
    window.setFixedSize(window.sizeHint())
    window.setMinimumWidth(700)
    
def switch_admin():
    global chkAdmin
    global window
    switch_admin_mode(chkAdmin.isChecked())
    
    
def start():
    global app
    global window
    global layout
    global MODE_ADMIN
    global SIZE_W
    global CONFIG_FILE
    global TESSERACT_PATH
    global USER_TESSERACT_PATH
    global PIXEL_PER_CM
    global JPEG_RATIO
    global USER_JPEG_RATIO
    global OLD_SIZE_W
    
    global POPPLER_MODE
    global USER_POPPLER_MODE
    global POPPLER_PATH
    global USER_POPPLER_PATH
    
    global console
    
    global lab_tesseract
    global lab_ratioJPEG
    global lab_opacity
    global lab_height
    
    global but_tif
    
    global input_height
    global input_tesseract
    global chkJPEG
    global chkAdmin
    global chkPoppler
    global input_ratioJPEG
    global OPACITY
    global USER_OPACITY
    global input_opacity
    global combobox_mode
    
    global labPoppler
    global inputPoppler
    
    
    global but_change_tesseract
    global but_change_poppler
    
    global chk_hsv
    
    global HSV_MODE
    global HSV_H_MIN
    global HSV_S_MIN
    global HSV_V_MIN
    global HSV_H_MAX
    global HSV_S_MAX
    global HSV_V_MAX

    global label_hsv_h_min
    global label_hsv_s_min
    global label_hsv_v_min
    global label_hsv_h_max
    global label_hsv_s_max
    global label_hsv_v_max
    
    global input_hsv_h_min
    global input_hsv_s_min
    global input_hsv_v_min
    global input_hsv_h_max
    global input_hsv_s_max
    global input_hsv_v_max
    
    
    try:
        MODE_ADMIN=False
        MODE_FOLDER=False
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        TESSERACT_PATH=config["SYSTEM"]["tesseract_path"]
        HEIGHT_IMAGE_CM=config["OUTPUT"]["height_image_cm"]
        PIXEL_PER_CM=config["OUTPUT"]["pixel_per_cm"]
        
        tmp_POPPLER=config["SYSTEM"]["poppler_mode"]
        
        POPPLER_PATH=config["SYSTEM"]["poppler_path"]
        POPPLER_MODE=False
        #if tmp_POPPLER.strip().lower()=="on":
        #    POPPLER_MODE=True
            
        
        
        USER_TESSERACT_PATH=TESSERACT_PATH.replace("\\","/").replace("'","").replace('"','').strip()
        
        JPEG_RATIO=config["OUTPUT"]["default_jpeg_ratio"]
        USER_JPEG_RATIO=JPEG_RATIO
        
        OPACITY=config["OUTPUT"]["text_opacity"]
        USER_OPACITY=OPACITY
        if os.path.isfile(USER_TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = USER_TESSERACT_PATH
            print("TESSERACT ON "+ USER_TESSERACT_PATH)
        else:
            print("TESSERACT NOT FOUND - SET IT MANUALLY !!!!")
            
        HSV_H_MIN=config["OUTPUT"]["hsv_h_min"]
        HSV_S_MIN=config["OUTPUT"]["hsv_s_min"]
        HSV_V_MIN=config["OUTPUT"]["hsv_v_min"]
        HSV_H_MAX=config["OUTPUT"]["hsv_h_max"]
        HSV_S_MAX=config["OUTPUT"]["hsv_s_max"]
        HSV_V_MAX=config["OUTPUT"]["hsv_v_max"]
        
        app = QApplication([])
        window = QWidget()
        window.setMinimumWidth(700)
        
        layout = QVBoxLayout()
        
        chkAdmin = QCheckBox("Admin mode")
        layout.addWidget(chkAdmin)
        chkAdmin.clicked.connect(switch_admin)
        
        lab_tesseract=QLabel()
        lab_tesseract.setText("Tesseract path :")
        
        layout.addWidget(lab_tesseract)
        
        
        input_tesseract=QLabel()
        input_tesseract.setText(TESSERACT_PATH)

        layout.addWidget(input_tesseract)
        
        but_change_tesseract=QPushButton('Change tesseract')
        layout.addWidget(but_change_tesseract)
        but_change_tesseract.clicked.connect(choose_tesseract)

        chkPoppler = QCheckBox("Set Poppler manually")
        layout.addWidget(chkPoppler)
        chkPoppler.clicked.connect(enable_poppler)
        chkPoppler.setChecked(POPPLER_MODE)
        
        
        
        labPoppler=QLabel()
        labPoppler.setText("Poppler path :")
        layout.addWidget(labPoppler)
        
        inputPoppler=QLabel()
        inputPoppler.setText(POPPLER_PATH)
        layout.addWidget(inputPoppler)
        
        but_change_poppler=QPushButton('Change Poppler')
        layout.addWidget(but_change_poppler)
        but_change_poppler.clicked.connect(choose_poppler)
        
        lab_mode=QLabel()
        lab_mode.setText("Select TIFF files or folders  :")
        layout.addWidget(lab_mode)
        
        combobox_mode = QComboBox()
        combobox_mode.addItems(['files_to_pdf', 'folder_to_pdf'])
        layout.addWidget(combobox_mode)
        combobox_mode.currentIndexChanged.connect(tiff_mode_changed)

        
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
        lab_height.setText("Height page (cm) :")
        layout.addWidget(lab_height)

        
        input_height=QLineEdit()
        input_height.setText(HEIGHT_IMAGE_CM)
        layout.addWidget(input_height)

        
        
        
        lab_opacity=QLabel()
        lab_opacity.setText("Text Opacity :")
        layout.addWidget(lab_opacity)

        
        input_opacity=QLineEdit()
        input_opacity.setText(OPACITY)
        layout.addWidget(input_opacity)

        chkJPEG = QCheckBox("Convert to JPG before creating PDF")
        layout.addWidget(chkJPEG)
        chkJPEG.clicked.connect(enable_jpeg_conversion)
        chkJPEG.setChecked(True)
        
        lab_ratioJPEG=QLabel()
        lab_ratioJPEG.setText("Ratio jpeg :")
        layout.addWidget(lab_ratioJPEG)

        
        
        input_ratioJPEG=QLineEdit()
        input_ratioJPEG.setText(USER_JPEG_RATIO)
        layout.addWidget(input_ratioJPEG)

        chk_hsv=QCheckBox("Normalize background")
        layout.addWidget(chk_hsv)
        chk_hsv.clicked.connect(enable_background_normalization)
        chk_hsv.setChecked(HSV_MODE)
        
        label_hsv_h_min= QLabel("H Min")
        layout.addWidget(label_hsv_h_min)
        input_hsv_h_min=QLineEdit(str(HSV_H_MIN))
        layout.addWidget(input_hsv_h_min)
        
        label_hsv_s_min= QLabel("S Min")
        layout.addWidget(label_hsv_s_min)
        input_hsv_s_min=QLineEdit(str(HSV_S_MIN))
        layout.addWidget(input_hsv_s_min)
        
        label_hsv_v_min= QLabel("V Min")
        layout.addWidget(label_hsv_v_min)
        input_hsv_v_min=QLineEdit(str(HSV_V_MIN))
        layout.addWidget(input_hsv_v_min)
        
        
        label_hsv_h_max= QLabel("H Max")
        layout.addWidget(label_hsv_h_max)
        input_hsv_h_max=QLineEdit(str(HSV_H_MAX))
        layout.addWidget(input_hsv_h_max)
        
        label_hsv_s_max= QLabel("S Max")
        layout.addWidget(label_hsv_s_max)
        input_hsv_s_max=QLineEdit(str(HSV_S_MAX))
        layout.addWidget(input_hsv_s_max)
        
        label_hsv_v_max= QLabel("V Max")
        layout.addWidget(label_hsv_v_max)
        input_hsv_v_max=QLineEdit(str(HSV_V_MAX))
        layout.addWidget(input_hsv_v_max)
        
        label_hsv_h_min.setVisible(False)
        input_hsv_h_min.setVisible(False)
        label_hsv_s_min.setVisible(False)
        input_hsv_s_min.setVisible(False)
        label_hsv_v_min.setVisible(False)
        input_hsv_v_min.setVisible(False)
        
        label_hsv_h_max.setVisible(False)
        input_hsv_h_max.setVisible(False)
        label_hsv_s_max.setVisible(False)
        input_hsv_s_max.setVisible(False)
        label_hsv_v_max.setVisible(False)
        input_hsv_v_max.setVisible(False)

        #input_ratioJPEG.setReadOnly(True)
        #input_ratioJPEG.setDisabled(True)
        
        but_launch=QPushButton('Launch OCR')
        layout.addWidget(but_launch)
        but_launch.clicked.connect(launch_ocr)
        
        
        
        console=QLabel()
        console.setText("Output")
        layout.addWidget(console)
        
        #switch_admin_mode(MODE_ADMIN)
        if MODE_ADMIN is False:
            lab_tesseract.setVisible(MODE_ADMIN)
            input_tesseract.setVisible(MODE_ADMIN)
            labPoppler.setVisible(MODE_ADMIN)
            inputPoppler.setVisible(MODE_ADMIN)
            
            lab_ratioJPEG.setVisible(MODE_ADMIN)
            lab_height.setVisible(MODE_ADMIN)
            lab_opacity.setVisible(MODE_ADMIN)
            input_height.setVisible(MODE_ADMIN)
            input_ratioJPEG.setVisible(MODE_ADMIN)
            input_opacity.setVisible(MODE_ADMIN)
            but_change_tesseract.setVisible(MODE_ADMIN)
            
            chkPoppler.setVisible(MODE_ADMIN)
            but_change_poppler.setVisible(MODE_ADMIN)
            
        app.exec()
        switch_admin_mode(MODE_ADMIN)
        
    except:    
        traceback.print_exception(*sys.exc_info())
if __name__ == '__main__':
    start()