from LineBotApi import check_push_message_method
from DataBaseApi import select_table

def good_morning():
    testDict = {
        '0':{
            'type':'Text',
            'text':'認命吧上班囉～'
        },
        '1':{
            'type':'Image',
            'img':'https://i.pinimg.com/originals/15/d6/06/15d606d56054969594bb4cf8e6d32bd9/200'
        }
    }

    workers = select_table('workers', 'worker_id')
    for w in workers:
        pushTo = w[0]
        if len(pushTo) > 0:
            check_push_message_method(testDict, pushTo)
    # fields = select_table('fightField', 'group_id')
    # image = 'https://placekeanu.com/200/150'
    # for f in fields:
    #     pushTo = f[0]
    #     if len(pushTo) > 0:
    #         push_image_message(pushTo, image)
    #         push_text_message(pushTo, '上班囉！各位社畜們～')

good_morning()