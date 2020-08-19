from LineBotApi import push_image_message, push_text_message
from DataBaseApi import select_table

def good_morning():
    workers = select_table('workers', 'worker_id')
    for w in workers:
        pushTo = w[0]
        if len(pushTo) > 0:
            push_text_message(pushTo, '下班沒～')
    fields = select_table('fightField', 'group_id')
    image = 'https://placekeanu.com/200/150'
    for f in fields:
        pushTo = f[0]
        if len(pushTo) > 0:
            push_image_message(pushTo, image)

good_morning()