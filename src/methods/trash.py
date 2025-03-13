@router.message(Command("member"))
@is_admin
async def member(message: Message, is_clb=False,**kwargs):
    await message.answer(f"""Команды:\n
команды не работают выключены в целях безопасности.                         
<span class="tg-spoiler">                         
/set_link - устанавливает ссылку на паблик в кнопку
Пример: /set_link https://t.me/+ajDEWo8xZW9jM2E3
Без аргумента вернет текущее значение
                         
/set_channel_id - установит Id канала для проверки подписки
Пример(публичный канал): /set_channel_id @durov
Пример(закрытый канал): /set_channel_id -1001006503122
Чтобы получить id закрытого канала перешли из него любой пост боту @username_to_id_bot. 
В обоих случаях необходимо выдать админку боту в канале, канал/добавить юзера/ пишем имя бота/ появляется кнопка сделать админом/ все галочки можно снять
Без аргумента вернет текущее значение
                         </span>""")
    


@router.message(Command("set_link"))
@is_admin
async def set_link(message: types.Message, command: CommandObject, is_clb=False, **kwargs):
    if command.args:  
        link = command.args
        await ConfigDatabase.set_value('link', link)
        await message.answer('Updated!')
    else:
        link = await ConfigDatabase.get_value('link')  
        await message.answer(text=f"link:\n\n<code>{link}</code>",parse_mode='HTML')

@router.message(Command("set_channel_id"))
@is_admin
async def set_channel_id(message: types.Message, command: CommandObject, is_clb=False, **kwargs):
    if command.args:  
        channel_id = command.args
        await ConfigDatabase.set_value('channel_id', channel_id)
        await message.answer('Updated!')
    else:
        channel_id = await ConfigDatabase.get_value('channel_id')  
        await message.answer(text=f"channel_id:\n\n<code>{channel_id}</code>",parse_mode='HTML')
