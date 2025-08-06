from pdf2image import convert_from_path
import numpy as np
import PIL 
import traceback
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QSlider, QLabel, QLineEdit
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
# pip install  PyMuPDF not fitz !
import pypdf
import re
from io import BytesIO

POPPLER_PATH="D:\\DEV\\CANATHIST\\POPPLER\\Release-24.02.0-0\\poppler-24.02.0\\Library\\bin"

app=None
window=None
layout=None
filename_pdf=None
filename_img=None

DEFAULT_QUAL=5
input_qual=None


def choose_pdf():
    global window
    global filename_pdf
    file_c = QFileDialog()
    filter = "PDF (*.PDF);;pdf (*.pdf)"
    filename_pdf,_ = file_c.getOpenFileName(window, "Open files", "", filter)
    print(filename_pdf)
    
def choose_images():
    global window
    global filename_img    
    file_name = QFileDialog()
    filter = "TIF (*.TIF);;tif (*.tif);;TIFF (*.TIFF);;tiff (*.tiff);;png (*.png);;PNG (*.PNG);;jpg (*.jpg);;JPG (*.JPG);;jpeg (*.jpeg);;JPEG (*.JPEG)"
    filename_img, _ = file_name.getOpenFileNames(window, "Open files", "", filter)
    print(filename_img)
    
def go():
    global filename_pdf
    global filename_img   
    global input_qual
    reader= pypdf.PdfReader(filename_pdf)
    pattern = re.compile(r"\.pdf", re.IGNORECASE)
    filename_pdf_w=pattern.sub("_new_bck.pdf", filename_pdf)
    print(filename_pdf_w)
    writer=pypdf.PdfWriter()
    
    print(len(reader.pages))
    if len(reader.pages)==len(filename_img):
        print("go_replace")
        i=0
        for i in range(0, len(reader.pages)):
            #print(filename_img[i])
            writer.add_page(reader.pages[i])
            #img=PIL.Image.open(filename_img[i],mode="r")            
            #reader.pages[i].images[0].replace(img)
        for i in range(0, len(writer.pages)):
            print(filename_img[i])
            img=PIL.Image.open(filename_img[i],mode="r")
            membuf = BytesIO()
            img.save(membuf, format="JPEG", optimize=True, quality=int(input_qual.text()))
            img2 = PIL.Image.open(membuf)
            writer.pages[i].images[0].replace(img2, quality=int(input_qual.text())) 

        writer.write(filename_pdf_w)
        print("done "+filename_pdf_w)
        """
        
        for page in reader.pages:
            img=PIL.Image.open(filename_img[i],mode="r")
            print(filename_img[i])
            page.ImageFile.replace(img)
            i=i+1
        """
    else:
        print("number of images differs from pages of PDF")
    
def start():
    global app
    global window
    global layout
    global input_qual
    
    try:
        app = QApplication([])
        window = QWidget()
        window.setMinimumWidth(700)
        
        layout = QVBoxLayout()
        
        but_pdf=QPushButton('Select PDF file  :')
        layout.addWidget(but_pdf)
        but_pdf.clicked.connect(choose_pdf)
        
        but_imgs=QPushButton('Select images  :')
        layout.addWidget(but_imgs)
        but_imgs.clicked.connect(choose_images)
        
        but_go=QPushButton('Go replace background  :')
        layout.addWidget(but_go)
        but_go.clicked.connect(go)
        
        lab_qual=QLabel()
        lab_qual.setText("Quality")
        layout.addWidget(lab_qual)
        
        input_qual=QLineEdit()
        input_qual.setText(str(DEFAULT_QUAL))
        layout.addWidget(input_qual)
        
        window.setLayout(layout)
        window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        window.show()    
        app.exec()
        
    except:    
        traceback.print_exception(*sys.exc_info())
    
if __name__ == '__main__':
    print("go")
    start()