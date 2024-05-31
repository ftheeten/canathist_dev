from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
#from rest_framework import permissionssudo
from django.core.cache import cache
import base64
#import tempfile
from django.core.files.temp import NamedTemporaryFile
import os.path
import shutil
import subprocess

#https://blog.logrocket.com/django-rest-framework-create-api/
#virtual env : source /var/www/html/wsi_dicom_rest/wsi_311/bin/activate

# Create your views here.
class WSIServiceView(APIView):

    #COMMAND_PATH="/home/franck/OrthancWSI-2.0/Applications/Build/OrthancWSIDicomizer --pyramid=1 --smooth=1 --levels=3 "
    COMMAND_PATH="/home/franck/OrthancWSI-2.0/Applications/Build/OrthancWSIDicomizer"
    def post(self, request, *args, **kwargs):
        #debug 
        cache.clear()
        img=request.data.get("img_base64")
        filename=request.data.get("filename")
        json_file=request.data.get("json_file")
        resp={}
        resp["status"]="uncomplete_params"
        if len(img)>0 and len(filename)>0 : #and len(json_file)>0:       
            #tmp_folder=settings.TMP_WSI_COPY_FOLDER
            #new_file=tmp_folder+"/"+filename.replace("/", "_")
            p_extension=filename.split(".")
            if len(p_extension)>1:
                p_prefix=p_extension[:-1]
                extension=p_extension[-1]
                new_file=NamedTemporaryFile(prefix='.'.join(p_prefix)+'_PREFIX_', suffix="."+extension)
                
                decoded = base64.b64decode(img)
                #print(decoded)
                f = open(new_file.name, 'wb')
                f.write(decoded)
                f.close()
                #time.sleep(60)
                #resp["img_base64"]=img
                #command=self.COMMAND_PATH+ " "+new_file.name
                #dbug
                #shutil.copyfile(new_file.name, "/home/franck/transfer/debug.jpg")
                result = subprocess.run([self.COMMAND_PATH, '--pyramid', "1", "--smooth", "1", "--levels", "3", new_file.name ], stdout=subprocess.PIPE, stderr = subprocess.PIPE,universal_newlines = True)
                resp["filename"]=filename
                resp["status"]="ok"
                resp["check"]=os.path.isfile(new_file.name)
                resp["size"]=os.path.getsize(new_file.name)
                resp["server_file"]=new_file.name
                resp["command"]=self.COMMAND_PATH
                resp["command_output"]=result.stdout
                resp["command_error"]=result.stderr
        return  Response(resp, status=status.HTTP_200_OK)

