# import time
# import datetime
# #今天星期几
# today=int(time.strftime("%w"))
# print(today)
# #某个日期星期几
# anyday=datetime.datetime(2020,8,20).strftime("%w")
# print(anyday)

# import random
# import requests as rq
# from time import sleep
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent


# img_name = '柯基'
# ua = UserAgent().random
# url = 'https://www.google.com.tw/search?q='+img_name+'&tbm=isch&tbs=isz'
# response = rq.get(url, headers={ 'User-Agent': ua })
# soup = BeautifulSoup(response.text, 'lxml')
# # imageBoxs = soup.select("div.islrc div")
# # imageBoxs = soup.findAll("div", class_="islrc")
# imageBoxs = soup.find_all("div", class_="isv-r PNCib MSM1fd BUooTd")
# dataIDs = []
# for box in imageBoxs:
#     # print(box.prettify())
#     dataID = ''
#     try:
#         dataID = (box['data-id'])
#     except:
#         pass
#     finally:
#         if dataID != '':
#             dataIDs.append(dataID)
# bigImageUrl = url + '#imgrc=' + random.choice(dataIDs)
# print(bigImageUrl)
# sleep(0.5)
# imageUA = UserAgent().random
# imageR = rq.get(bigImageUrl, headers={ 'User-Agent': imageUA })
# imageSoup = BeautifulSoup(imageR.text, 'lxml')
# # imageBoxs = imageSoup.find_all("div", class_="T1diZc KWE8qe")
# imageBoxs = imageSoup.find_all("div", class_="l39u4d")

# imageUrls = []
# for i in imageBoxs:
    # print(i.prettify())
#     imageUrl = ''
#     try:
#         imageUrl = (i['href'])
#     except:
#         pass
#     finally:
#         if imageUrl != '' and imageUrl.find('/imgres?') >= 0 and imageUrl.find('https') >= 0:
#             start = imageUrl.find('/imgres?') + len('/imgres?')
#             end = imageUrl.find('&amp;')
#             print(imageUrl[start:end])
#             imageUrls.append(imageUrl[start:end])
# print(imageSoup.prettify())