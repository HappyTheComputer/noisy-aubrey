def reply_spideypool_party(event):
    text = event.message.text
    if text == '測試':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='不要以為你是' + profile.display_name + '就了不起哦！')
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="你是誰啊？"))
    elif text == '開修羅場':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text= profile.display_name + '要趕稿囉！')
                ]
            )
    else:
        pass