import os
import pathlib
import random
import errno

import requests as rq
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

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
    # check_image_finder()

    url = 'https://www.google.com.tw/search?q=' + searchKey + '&tbm=isch'
    ua = UserAgent().random
    # 開始搜尋跟下載
    response = rq.get(url, headers={ 'User-Agent': ua })
    soup = BeautifulSoup(response.text, 'lxml')
    img_arr = soup.find_all("img")
    img_success_num = 0
    img_file_arr = []
    for i in img_arr:
        if img_success_num >= lim:
            break
        tmp_content=''
        try:
            tmp_content=(i['data-src'])
        except:
            pass
        finally:
            if tmp_content != '' and tmp_content.find('http') >= 0 and tmp_content.find('/images') >= 0:
                img_file_arr.append(tmp_content)
                # image_path = download_image(tmp_content, img_success_num)
                # img_file_arr.append(image_path)
                img_success_num += 1

    return img_file_arr

def download_image(content, index):
    r = rq.get(content, stream=True)
    img_path = 'imgfile_%02d.png' %(index)
    print(img_path)
    with open(img_path,'wb') as file:
        file.write(r.content)
        file.close() 
    return img_path
