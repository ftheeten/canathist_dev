from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QLineEdit, QLabel, QSpinBox, QDoubleSpinBox
from PySide6.QtCore import Qt
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas
import rioxarray as rxr
from rasterio.plot import plotting_extent
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import shapely
from matplotlib_scalebar.scalebar import ScaleBar
from pyproj import Proj, transform, CRS, Transformer
from shapely.ops import nearest_points
import numpy as np
import pandas
import rasterio
import re
import math
import chardet

class DistriMapGUI(QApplication):

    PROJ_4_PATH_PARAM="C:\\OSGeo4W\\share\\proj"
    PROJ_4_PATH=None
    
    """
    SRC_EPSG_PARAM="32725"
    SRC_EPSG=None
    """
    
    min_x=None
    max_x=None 
    min_y=None
    max_y=None
    
    in_tiff=None
    in_csv=None
    out_img=None
    
    raster_data = None
    raster_data_extent = None
    transformer=None
    
    bbox_conv=None
    xticks=None
    jticks=None
    xlabels=None
    jlabels=None    
    
    def __init__(self):
        super(DistriMapGUI, self).__init__([])
        self.window = QWidget()
        self.init_gui()
        self.window.show()
        self.exec()
        
    def choose_input_proj4(self):
        folder_name = QFileDialog()
        selected_directory = folder_name.getExistingDirectory()
        self.PROJ_4_PATH=selected_directory
        self.label_input_proj4.setText("PROJ4 path : "+self.PROJ_4_PATH) 
        
    def choose_input(self):
        file_name = QFileDialog()
        filter = "TIF (*.TIF *.TIFF);;GEOTIFF (*.GEOTIF *.GEOTIFF);;"
        self.in_tiff, _ = file_name.getOpenFileName(self.window, "Open files", "", filter)
        self.label_input_raster.setText("Input raster :"+self.in_tiff)
        
    def choose_input_csv(self):
        file_name = QFileDialog()
        filter = "CSV (*.CSV);;TXT (*.TXT);;"
        self.in_csv, _ = file_name.getOpenFileName(self.window, "Open files", "", filter)
        self.label_input_csv.setText("Input raster :"+self.in_csv)
        
    def choose_output_folder(self):
        folder_name = QFileDialog()
        self.out_img = folder_name.getExistingDirectory()
        self.label_output_folder.setText("Output folder : "+self.out_img) 

    def proceed(self):
        print("proceed")
        os.environ["PROJ_LIB"]=self.PROJ_4_PATH
        
        """
        self.SRC_EPSG=int(self.SRC_EPSG_PARAM)
        """
        
        self.min_x=float((self.input_min_x.text() or "").replace(",", "."))
        print(self.min_x)
        
        self.max_x=float((self.input_max_x.text() or "").replace(",", "."))
        print(self.max_x)
        
        self.min_y=float((self.input_min_y.text() or "").replace(",", "."))
        print(self.min_y)
        
        self.max_y=float((self.input_max_y.text() or "").replace(",", "."))
        print(self.max_y)
        if len( str(self.min_x))>0 and len( str(self.min_y))>0 and len( str(self.max_x))>0 and len( str(self.max_x))>0 and (self.in_tiff is not None) and (self.in_csv is not None) and (self.out_img is not None) :
            rawdata = open(self.in_csv, "rb").read()
            guess = chardet.detect(rawdata)
            print(guess)
            if 'encoding' in guess:
                self.transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
                bbox_all=[self.min_y, self.max_y, self.min_x, self.max_x]
                #bbox_all=[28.9, 31, -4.7, -2.2]
                df_dist=pandas.read_csv(self.in_csv, sep='\t', encoding=guess['encoding'].upper())
                self.raster_data = rxr.open_rasterio(self.in_tiff, masked=True).rio.reproject("epsg:3857")
                self.raster_data_extent = plotting_extent(self.raster_data[0], self.raster_data.rio.transform())
                bbox_1=self.transformer.transform(bbox_all[0], bbox_all[2])
                bbox_2=self.transformer.transform(bbox_all[0], bbox_all[3])
                bbox_3=self.transformer.transform( bbox_all[1], bbox_all[3])
                bbox_4=self.transformer.transform(bbox_all[1], bbox_all[2])
                self.bbox_conv=[bbox_1[0],bbox_4[0],bbox_1[1], bbox_3[1]]
                self.xticks=[]
                self.jticks=[]
                self.xlabels=[]
                self.jlabels=[]
                i=bbox_all[0]
                while i <= bbox_all[1] :
                    if (i % 0.5) ==0:
                        pt_coord=self.transformer.transform(i,bbox_all[2])
                        self.xticks.append(pt_coord[0])
                        self.xlabels.append(i)
                    i=round(i+0.1,2)
                j=bbox_all[2]
                while j <= bbox_all[3] :
                    if (j % 0.5) ==0:
                        pt_coord=self.transformer.transform(bbox_all[0],j)
                        self.jticks.append(pt_coord[1])
                        self.jlabels.append(j)
                    j=round(j+0.1,2)
                """
                for i, row in df_dist.iterrows():
                    print(row)
                """
                list_sp=df_dist.key.unique()
                print(list_sp)
                for sp in list_sp:
                    dist=df_dist[df_dist["key"].str.lower()==sp.lower()]
                    self.go_map(dist, sp)
                    
    def isfloat(self, num):
        num=num.replace(",",".")
        try:
            float(num)
            return True
        except ValueError:
            return False
                    
    def go_map(self, dist, name_map):
        list_points=[]
        for index2, row2 in dist.iterrows():
            if len(str(row2["longitude"]))>0 and len(str(row2["latitude"]))>0 :
                
                if self.isfloat(str(row2["longitude"])) and self.isfloat(str(row2["latitude"])):
                    pt=shapely.geometry.Point(self.transformer.transform(float(str(row2["longitude"]).replace(",",".")), float(str(row2["latitude"]).replace(",","."))))
                    list_points.append(pt) 
        if len(list_points)>0:
            self.go_plot(  name_map,list_points)
            
    def go_plot( self, name_map, points):     
        f, ax = plt.subplots(figsize=(7,7))
        ep.plot_rgb(self.raster_data.values,
                    rgb=[0, 1, 2],
                    ax=ax,               
                    extent=self.raster_data_extent)
        
        p_points=geopandas.GeoDataFrame(geometry=points)
        p_points.set_crs(epsg=3857, inplace=True)
        p_points.plot(ax=ax,  color="black", markersize=140, edgecolor="white" )    
        ax.set_xticks(self.xticks)
        ax.set_yticks(self.jticks)
        ax.set_xticklabels(self.xlabels)
        ax.set_yticklabels(self.jlabels)
        ax.set_xlim(self.bbox_conv[0], self.bbox_conv[1])
        ax.set_ylim(self.bbox_conv[2], self.bbox_conv[3])
        ax.add_artist(ScaleBar(
            dx=1,
            box_alpha=0.1,
            location='lower left'
        ))    
        name_file=self.format_filename(name_map)+".svg"
        print(name_file)
        plt.savefig(self.out_img+"\\"+name_file, dpi=600, bbox_inches='tight')
        plt.close('all')
        
    def format_filename(self, name):
        name_array=str(name).replace("&","").replace(" ex ","").split(" ")
        new_name=[]
        i=0
        for tmp in name_array:
            if not (("(" in tmp) or (")" in tmp) or tmp.isnumeric() or (tmp.lower()!=tmp and i>1)):
                new_name.append(tmp.replace(".",""))
                i=i+1
        returned= "_".join(new_name).replace(" ","_")
        returned = re.sub(' +', ' ', returned)
        if  returned is not None:
            returned=returned.replace("_f_","")
            returned=returned.strip("_")
        returned=returned.strip("_")
        returned=returned.strip("_de")
        return returned
            
    def init_gui(self):
        self.PROJ_4_PATH=self.PROJ_4_PATH_PARAM
        self.layout = QVBoxLayout()
        
        self.label_input_proj4=QLabel("PROJ4 path :")
        self.layout.addWidget(self.label_input_proj4)
        self.label_input_proj4.setText("PROJ4 path : "+self.PROJ_4_PATH)
        
        
        self.but_input_proj4= QPushButton('Path for PROJ4')
        self.layout.addWidget(self.but_input_proj4)
        self.but_input_proj4.clicked.connect(self.choose_input_proj4)
        
        self.label_input_raster=QLabel("Input raster :")
        self.layout.addWidget(self.label_input_raster)
        
        self.but_input_files= QPushButton('Input files (background raster)')
        self.layout.addWidget(self.but_input_files)
        self.but_input_files.clicked.connect(self.choose_input)
        
        self.label_input_csv=QLabel("Input CSV Points :")
        self.layout.addWidget(self.label_input_csv)
        
        self.but_input_files_csv= QPushButton('Input files (CSV points)')
        self.layout.addWidget(self.but_input_files_csv)
        self.but_input_files_csv.clicked.connect(self.choose_input_csv)
        
        self.label_min_y=QLabel("Minimal longitude :")
        self.layout.addWidget(self.label_min_y)
        self.input_min_y=QLineEdit()
        self.layout.addWidget(self.input_min_y)
        
        self.label_min_x=QLabel("Minimal latitude :")
        self.layout.addWidget(self.label_min_x)
        self.input_min_x=QLineEdit()
        self.layout.addWidget(self.input_min_x)
        
        self.label_max_y=QLabel("Maximal longitude :")
        self.layout.addWidget(self.label_max_y)
        self.input_max_y=QLineEdit()
        self.layout.addWidget(self.input_max_y)
        
        self.label_max_x=QLabel("Maximal latitude :")
        self.layout.addWidget(self.label_max_x)
        self.input_max_x=QLineEdit()
        self.layout.addWidget(self.input_max_x)
        
        """
        self.label_epsg=QLabel("Source EPSG :")
        self.layout.addWidget(self.label_epsg)
        self.input_src_epsg=QLineEdit()
        self.input_src_epsg.setText(self.SRC_EPSG_PARAM)
        self.layout.addWidget(self.input_src_epsg)
        """
        
        self.label_output_folder=QLabel("Output folder :")
        self.layout.addWidget(self.label_output_folder)
        
        
        self.but_output_files= QPushButton('Choose output')
        self.layout.addWidget(self.but_output_files)
        self.but_output_files.clicked.connect(self.choose_output_folder)
        
        self.but_proceed= QPushButton('Proceed')
        self.layout.addWidget(self.but_proceed)
        self.but_proceed.clicked.connect(self.proceed)
        
        
        
        
        self.window.setLayout(self.layout)
        self.window.setFixedSize(self.window.sizeHint())
        self.window.setMinimumWidth(700)
        
app=DistriMapGUI()