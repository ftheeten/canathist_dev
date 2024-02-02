import os
import rioxarray
from rioxarray.rioxarray import XRasterBase
from rasterio.plot import plotting_extent

import keras_ocr

import cv2
import math
import matplotlib.pyplot as plt
import earthpy.plot as ep
import io
from PIL import Image
import numpy as np
import cv2
import datetime
import time
from shapely.geometry import Polygon, Point
import pandas
#import openpyxl

os.environ["PROJ_LIB"]="C:\\OSGeo4W\\share\\proj"
PIPELINE=None
#RESULTS={}
I_RESULT=0
#RESULTS_CLUSTERS={}
#I_RESULT_CLUSTERS=0
fp = "C:\\DEV\\CANATHIST\\cartes_cedric\\img20240131_16202471_modified_georef_3.tif"
out_xls= "C:\\DEV\\CANATHIST\\cartes_cedric\\img20240131_16202471_modified_georef_3_georef.xlsx"
'''
def calculate_iou(box_1, box_2):
    poly_1 = Polygon(box_1)
    poly_2 = Polygon(box_2)
    iou = poly_1.intersection(poly_2).area / poly_1.union(poly_2).area
    return iou
'''
    
def get_boxes(list_w, list_h, width, height):
    returned=[]
    for i in range(0, len(list_w)-1):
        for j in range(0, len(list_h)-1):
            x_min=int(math.floor(list_w[i]))
            y_min=int(math.floor(list_h[j]))
            x_max=int(math.floor(list_w[i+1]))
            y_max=int(math.floor(list_h[j+1]))
            returned.append((x_min,y_min,x_max, y_max))
    return returned

def cut_image(image, bbox, geo_x_min_map, geo_y_min_map, res_x, res_y, pipeline, cv_obj, origin, df):
    #global RESULTS
    global I_RESULT
    print(bbox)
    print(geo_x_min_map)
    print(geo_y_min_map)
    x_min_tmp, y_min_tmp, x_max_tmp, y_max_tmp=bbox
    cropped_image = cv_obj[ y_min_tmp:y_max_tmp, x_min_tmp:x_max_tmp]
    offset_x=x_min_tmp
    offset_y=y_min_tmp
    print("x")
    print(offset_x)
    print(offset_x*res_x)
    print("y")
    print(offset_y)
    print(offset_y*res_y)
    print("ori_x")
    tile_geo_x=geo_x_min_map+(offset_x*res_x)
    print(tile_geo_x)
    print("ori_y")
    tile_geo_y=geo_y_min_map-(offset_y*res_y)
    print(tile_geo_y)
    kobj=keras_ocr.tools.read(cropped_image)
    prediction_groups = pipeline.recognize([kobj])
    i=0
    for pred in prediction_groups:
        print(i)
        print("---------------------------------------------------------------")
        for pred2 in pred:
            print("====>")
            #print(pred2)
            if len(pred2)>=2:
                text=pred2[0]
                box=pred2[1]
                print(text)
                print(box)
                if len(box)>=4:
                    b1=box[0]
                    b2=box[1]
                    b3=box[2]
                    b4=box[3]
                    map_b1=[tile_geo_x+((b1[0])*res_x), tile_geo_y-((b1[1])*res_y)]
                    map_b2=[tile_geo_x+((b2[0])*res_x), tile_geo_y-((b2[1])*res_y)]
                    map_b3=[tile_geo_x+((b3[0])*res_x), tile_geo_y-((b3[1])*res_y)]
                    map_b4=[tile_geo_x+((b4[0])*res_x), tile_geo_y-((b4[1])*res_y)]
                    print(map_b1)
                    print(map_b2)
                    print(map_b3)
                    print(map_b4)
                    obj={}
                    obj["label"]=text
                    
                    obj["bbox"]=[map_b1, map_b2, map_b3, map_b4]
                    poly_tmp = Polygon(obj["bbox"])
                    obj["area"]=poly_tmp.area
                    obj["longitude"]=poly_tmp.centroid.x
                    obj["latitude"]=poly_tmp.centroid.y
                    distance_from_origin=poly_tmp.centroid.distance(origin)
                    obj["distance_from_origin"]=distance_from_origin
                    df= pandas.concat([df, pandas.DataFrame([obj])], ignore_index=True)
                    #RESULTS[I_RESULT]=obj
                    I_RESULT=I_RESULT+1
                    
        i=i+1
    return df
    #cv2.imshow('view_'+str(time.time()),cropped_image)
    #cv2.waitKey(0)

'''
def calculate_intersection(p_results):
    for key , item in p_results.items():
        for key2 , item2 in p_results.items():
            if key != key2:
                #print("INTER FOR "+str(key)+" "+str(key2))
                bbox1=item["bbox"]
                bbox2=item2["bbox"]
                inter=calculate_iou(bbox1, bbox2)
                #print(inter)
'''

def tile(fp, out_xls, tile_h, tile_w, offset_h, offset_w,  ratio_offset_2ndpass=0.75):
    df = pandas.DataFrame()
    src = rioxarray.open_rasterio(fp, masked=True).rio.reproject("epsg:4326")
    src_cv2=cv2.imread(fp)
    geo_obj=XRasterBase(src)
    global PIPELINE
    PIPELINE = keras_ocr.pipeline.Pipeline()
    print(geo_obj.bounds())
    print(geo_obj.height)
    print(geo_obj.width)
    print(geo_obj.bounds())
    print(geo_obj.height)
    print(geo_obj.width)
    res_x=(geo_obj.bounds()[2]-geo_obj.bounds()[0])/geo_obj.width
    res_y=(geo_obj.bounds()[3]-geo_obj.bounds()[1])/geo_obj.height
    print(res_x)
    print(res_y)
    x_min=geo_obj.bounds()[0]
    y_min=geo_obj.bounds()[1]
    x_max=geo_obj.bounds()[2]
    y_max=geo_obj.bounds()[3]
    shape_ori=Point(x_min, y_max)
    list_w=[]
    list_w_offset=[]
    list_h=[]
    list_h_offset=[]
    if geo_obj.width > tile_w:
        list_w_offset.append(0)
        for i in range(0, geo_obj.width, tile_w):
            list_w.append(i)
            offset_w_calc=i+math.floor(ratio_offset_2ndpass*tile_w)
            if offset_w_calc<(geo_obj.width-tile_w):
                list_w_offset.append(offset_w_calc)
        list_w.append(geo_obj.width)
        if len(list_w_offset)==1:
            list_w_offset.append(ratio_offset_2ndpass*tile_w)
            list_w_offset.append(geo_obj.width)
        else:
            list_w_offset.append(list_w_offset[len(list_w_offset)-1]+tile_w)
    else:
        list_w.append(0)
        list_w.append(geo_obj.width)
    print(list_w)
    print(list_w_offset)
    if geo_obj.height > tile_h:
        list_h_offset.append(0)
        for i in range(0, geo_obj.height, tile_h):
            list_h.append(i)
            offset_h_calc=i+math.floor(ratio_offset_2ndpass*tile_h)
            if offset_h_calc<(geo_obj.height-tile_h):
                list_h_offset.append(offset_h_calc)
        list_h.append(geo_obj.height)
        if len(list_h_offset)==1:
            list_h_offset.append(ratio_offset_2ndpass*tile_h)
            list_h_offset.append(geo_obj.height)
        else:
            list_h_offset.append(list_h_offset[len(list_h_offset)-1]+tile_h)
    else:
        list_h.append(0)
        list_h.append(geo_obj.height)            
    print(list_h)
    print(list_h_offset)        
    bboxes=get_boxes(list_w, list_h, geo_obj.width, geo_obj.height)
    bboxes_offset=[]
    if len(list_w_offset)>0 and len(list_h_offset)>0:
        bboxes_offset=get_boxes(list_w_offset, list_h_offset, geo_obj.width, geo_obj.height)
    print(bboxes)
    print(bboxes_offset)
    for box in bboxes:
        df=cut_image(src, box, x_min, y_max, res_x, res_y, PIPELINE, src_cv2, shape_ori, df)
    for box in bboxes_offset:
        df=cut_image(src, box, x_min, y_max, res_x, res_y, PIPELINE, src_cv2, shape_ori, df)
    #print(RESULTS)
    #calculate_intersection(RESULTS)
    #cv2.waitKey(0)
    #for index, row in df.iterrows():
    #    print(row) 
    print(I_RESULT)
    df.to_excel(out_xls)
#main(fp)    
        
tile(fp, out_xls, 1000, 1000, 0, 0)
    
