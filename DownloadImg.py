import re
import os
import pathlib
import base64
import random

from requests_html import HTMLSession

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

def check_image_finder():
    pathlib.Path(static_tmp_path).mkdir(parents=True, exist_ok=True)
    #清除資料夾裡的 jpg 及 png 檔
    filelist = [ f for f in os.listdir(static_tmp_path) if f.endswith(".jpg") or f.endswith(".gif") or f.endswith(".png")]
    for f in filelist:
        os.remove(os.path.join(static_tmp_path, f))

def search_image(searchKey, lim = 1):
    check_image_finder()

    url = 'https://www.google.com.tw/search?q=' + searchKey + '&tbm=isch&tbs=isz%3Am'
    # 開始搜尋跟下載
    session = HTMLSession()
    r = session.get(url)
    r.html.render(sleep=3, scrolldown=1, wait=2)
    img_arr = r.html.find("img")
    img_success_num = 0
    img_file_arr = []
    for i in img_arr:
        if img_success_num >= lim:
            break
        tmp_content=''
        try:
            tmp_content=(i.attrs['src'])
        except:
            pass
        finally:
            if tmp_content != '' and tmp_content.find('http') < 0 and tmp_content.find('/images') < 0:
                image_path = download_image(tmp_content, img_success_num)
                img_file_arr.append(image_path)
                img_success_num += 1

    if len(img_file_arr) == 1:
        return img_file_arr[0]
    else:
        return img_file_arr
    

def download_image(content, index):
    img_path = '%s/imgfile_%02d' %(static_tmp_path, index)
    if content.find("jpeg")>-1:
        img_path += '.jpg'
    elif content.find("gif")>-1:
        img_type += '.gif'
    else:
        img_type += '.png'
    print(img_path)
    with open(img_path,'wb') as file:
        base64_data = re.sub('^data:image/.+;base64,', '', content)
        byte_data = base64.b64decode(base64_data)
        file.write(byte_data)
        file.flush()
        file.close() 
    return img_path
