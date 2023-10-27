#https://stackoverflow.com/questions/31432090/pyside-password-field-not-working
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel, QCheckBox, QMessageBox, QComboBox, QSizePolicy
from PySide6.QtCore import Qt
import os
import io
import traceback
import sys
import json

import configparser

from bibtexparser.bparser import BibTexParser
import requests
from requests.auth import HTTPBasicAuth


app=None
window=None
layout=None
CONFIG_FILE="config.cfg"
URL_ENDPOINT=""

but_load_bibtex=None
input_bibtex=None
bib_text_path=None

but_choose_json=None
input_json_path=None
bib_json_path=None

input_url_end_point=None
input_url_end_point_user=None
input_url_end_point_password=None

tmp_obj=None



SRC_FILE="D:\\DEV\\CANATHIST\\python\\bibtex\\sources\\export.bib"
root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
auth_mars = HTTPBasicAuth('', '')


def post_data():
    global input_url_end_point
    global input_url_end_point_user
    global input_url_end_point_password
    global auth_mars
    global bib_text_path
    global tmp_obj
    p_url=input_url_end_point.text()
    user=input_url_end_point_user.text()
    pwd=input_url_end_point_password.text()
    auth_mars = HTTPBasicAuth(user, pwd)
    if len(bib_text_path)>0:
        tmp_obj=conv_bib(bib_text_path)
        print(tmp_obj)
        data=requests.post(p_url, headers={'accept':'application/json', 'Accept-Charset':'utf-8'},auth=auth_mars, data=json.dumps(tmp_obj), verify=False)
        print("done")
        print(data)

def explode_authors(p_entry):
    if 'author' in p_entry:
        list_auth=p_entry['author'].split(' and ')
        #print(list_auth)
        returned = [s.strip() for s in list_auth]
        p_entry['author']=returned

  
    

def handle_entry(p_entry):
    print(p_entry)
    explode_authors(p_entry)
    
    

def choose_bibtex():
    global input_bibtex
    global bib_text_path
    file_name = QFileDialog()
    filter = "bib (*.bib);;others (*.*)"
    bib_text_path,_ = file_name.getOpenFileName(window, "Open files", "", filter)
    input_bibtex.setText(bib_text_path)
    
def choose_json():
    global input_json_path
    global bib_json_path
    file_name = QFileDialog()
    
    bib_json_path = file_name.getSaveFileName(window,  caption='Select a data file', filter='JSON File (*.json)')[0]
    input_json_path.setText(bib_json_path)
        
def conv_bib(p_path):
    parser = BibTexParser()
    file = open(p_path, "r")
    library = parser.parse_file(file)
    print(library)
    entries=[]
    for i in range(0,len(library.entries) ):
        print(i)
        entry=library.entries[i]
        handle_entry(entry)
        entries.append(entry)
    file.close()
    return entries
   
def create_json():
    global bib_text_path
    global bib_json_path
    global tmp_obj
    if len(bib_text_path)>0 and len(bib_json_path)>0:
        fp=open(bib_json_path, 'w')
        tmp_obj=conv_bib(bib_text_path)
        print(tmp_obj)
        json.dump(tmp_obj, fp)
        fp.close()
        
        
def start():
    global app
    global window
    global layout
    global CONFIG_FILE
    global but_load_bibtex
    global input_bibtex
    
    global but_choose_json
    global input_json_path
    
    global input_url_end_point
    global input_url_end_point_user
    global input_url_end_point_password
    
    try:
        print("start")
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        url_endpoint=config["TARGET"]["post_endpoint"]
        
        app = QApplication([])
        window = QWidget()
        window.setMinimumWidth(700)
        layout = QVBoxLayout()
        
        but_load_bibtex=QPushButton('Load file')
        layout.addWidget(but_load_bibtex)
        but_load_bibtex.clicked.connect(choose_bibtex)
        
        input_bibtex=QLabel()
        layout.addWidget(input_bibtex)
        
        
        but_choose_json=QPushButton('Choose output json')
        layout.addWidget(but_choose_json)
        but_choose_json.clicked.connect(choose_json)
        
        input_json_path=QLabel()
        layout.addWidget(input_json_path)
        
        but_create_json=QPushButton('Generate JSON')
        layout.addWidget(but_create_json)
        but_create_json.clicked.connect(create_json)
        
        lab_endpoint=QLabel()
        lab_endpoint.setText("URL Zope")
        layout.addWidget(lab_endpoint)
        
        input_url_end_point=QLineEdit()
        input_url_end_point.setText(url_endpoint)
        layout.addWidget(input_url_end_point)
        
        lab_endpoint_user=QLabel()
        lab_endpoint_user.setText("Zope User")
        layout.addWidget(lab_endpoint_user)
        
        input_url_end_point_user=QLineEdit()
        layout.addWidget(input_url_end_point_user)
        

        lab_endpoint_password=QLabel()
        lab_endpoint_password.setText("Zope password")
        layout.addWidget(lab_endpoint_password)
        
        input_url_end_point_password=QLineEdit()
        input_url_end_point_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(input_url_end_point_password)
        
        but_send_bibtex_zope=QPushButton('Send to Zope')
        layout.addWidget(but_send_bibtex_zope)
        but_send_bibtex_zope.clicked.connect(post_data)
        
        window.setLayout(layout)
        window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        window.show()           
        app.exec()
    except:    
        traceback.print_exception(*sys.exc_info())
if __name__ == '__main__':
    start()
#conv_bib(SRC_FILE)
