# import time
# import datetime
# #今天星期几
# today=int(time.strftime("%w"))
# print(today)
# #某个日期星期几
# anyday=datetime.datetime(2020,8,20).strftime("%w")
# print(anyday)

from DownloadImg import search_image
path = search_image('dog', 10)