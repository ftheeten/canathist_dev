import base64
import requests


IMG="C:\\Users\\ftheeten\\Downloads\\kouilou_lefini_bridge_satellite.jpg"
FILENAME="kouilou_lefini_bridge_satellite_corr.png"
URL = "https://naturalheritage.africamuseum.be/wsidicomizer_rest/api/"
CMD="./OrthancWSIDicomizer --pyramid=1 --smooth=1 --levels=3 --folder=/home/franck /home/franck/vlcsnap-2022-07-06-22h58m29s170.png"


with open(IMG, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
    print(encoded_string)
    data = {'img_base64':encoded_string,
            'filename':"kouilou_lefini_bridge_satellite.jpg"
    }
    r = requests.post(url = URL, data = data)
    print(r)
    print(r.text)