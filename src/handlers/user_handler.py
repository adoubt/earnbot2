import asyncio
from datetime import datetime,timezone
from loguru import logger
from aiogram import Router, F
from aiogram.filters import Command,StateFilter, CommandObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery,LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from src.handlers.decorators import new_user_handler,is_admin
from src.keyboards import user_keyboards
from src.methods.database.users_manager import UsersDatabase
from src.methods.database.videos_manager import VideosDatabase
from src.methods.database.config_manager import ConfigDatabase
from src.methods.utils import parse_callback_data, is_valid_email, get_file_id, get_bot_username,handle_send_ad, time_view, AdStateFilter
from src.misc import bot, CHANNEL_LINK, CHANNEL_ID,TIME_REQUEST,WATCHED_VIDEOS_THRESHOLD,AD_MSG_WITHDRAW,LOG_CHANNEL_LINK, LOG_CHANNEL_ID
router =  Router()



@router.message(Command("start"))
@new_user_handler
async def start_handler(message: Message, is_clb=False,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    requested = await UsersDatabase.get_value(user_id,'requested')
    await message.answer("""Nuestra empresa tiene un acuerdo con una agencia de publicidad para promocionar un vídeo en TikTok 📈
 
Por lo tanto, estamos dispuestos a pagar a cada usuario por ver vídeos cortos subidos por este bot.
 
⚠️ Tienes que ver los vídeos para ser recompensado. Los vídeos duran entre 10 y 15 segundos
 
💰 Puedes ganar hasta <b>50 Sol</b> diariamente viendo vídeos
 
Para empezar, pulse el botón "<b>Ver vídeos y ganar dinero 📺</b>".""",parse_mode="HTML",reply_markup=user_keyboards.get_start_kb(requested))
    
#Обработчик для кнопки "Смотреть видео"

@router.message(F.text == "Ver vídeos y ganar dinero 📺")
async def videos(message:Message, is_clb=False,**kwargs):

    await message.answer("""Nuestra empresa tiene un contrato con una agencia de publicidad que necesita promocionar vídeos en TikTok 📈

Por lo tanto, estamos dispuestos a pagar a cada uno de nuestros usuarios por ver vídeos cortos enviados por este bot.
 
⚠ Tienes que ver el vídeo hasta el final para conseguir la recompensa. La duración del vídeo es de 10-15 segundos.
 
💰 Cada día puedes ganar hasta <b>50 Sol</b> viendo vídeos
 
Pulse el botón "<b>Empezar a ver 📺</b>" para comenzar.""", parse_mode="HTML", reply_markup=user_keyboards.get_videos_kb())
     
#Обработчик для кнопки "Canal"
@router.message(F.text == "Canal")
async def channel(message:Message, is_clb=False,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    await bot.send_message(user_id, text='Únete a nuestro canal y te enseñaremos a ganar dinero!',reply_markup=user_keyboards.get_channel_kb(CHANNEL_LINK))

#Обработчик для кнопки "Правила"
@router.message(F.text == "Reglas 🎯")
async def rules(message:Message, is_clb=False,**kwargs):
    await message.answer("""Nuestra empresa tiene un acuerdo con una agencia de publicidad para promocionar un vídeo en TikTok 📈
 
Por lo tanto, estamos dispuestos a pagar a cada usuario por ver vídeos cortos subidos por este bot.
 
⚠️ Tienes que ver los vídeos para ser recompensado. Los vídeos duran entre 10 y 15 segundos
 
💰 Puedes ganar hasta <b>50 Sol</b> diariamente viendo vídeos
 
Para empezar, pulse el botón "<b>Ver vídeos y ganar dinero 📺</b>".""",parse_mode="HTML")

#ОБработчик для кнопки "Профиль"
@router.message(F.text == "📱 Mi perfil")
async def profile(message:Message, is_clb=False,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    data = await UsersDatabase.get_user(user_id)
    balance, referrals, rereferrals = data[3], data[5], data[6]
    await message.answer(f"""Su saldo: <b>{balance} Sol</b>
Número de amigos invitados: <b>{referrals}</b>
Usuarios invitados por tus amigos: <b>{rereferrals}</b>""",parse_mode="HTML")
    

#ОБработчик ля кнопки "Вывод"

@router.message(F.text == "Retirada de dinero  🏧")
async def withdraw(message:Message, state: FSMContext, is_clb=False,**kwargs):
    user_id = message.chat.id 
    data = await UsersDatabase.get_user(user_id)
    requested = data[15]
    if requested == 1:
        requested_time =  datetime.strptime(data[17], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        time_now = datetime.now(timezone.utc)
        time_diff = (time_now - requested_time).total_seconds()

        if time_diff < TIME_REQUEST:
            text = "Con éxito ✅ \nSu solicitud ha sido enviada ✅ \nEspere 48 horas para una respuesta"
        else:
            text = ("""Desafortunadamente, experimentamos problemas técnicos,
¡nos disculpamos!
                    
Su dinero será acreditado a su cuenta dentro de las 72 horas""")

        await message.answer(text=text)
        return
    
    watched_videos = data[11]
    ismember = data[13]

    if watched_videos < WATCHED_VIDEOS_THRESHOLD:
        await message.answer(
            "❗️ Debes ver al menos 5 vídeos para retirar fondos.\n\nHaz clic en Empezar a ver 📺 y empieza ya.",
            reply_markup=user_keyboards.get_videos_kb())
        return
    chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

    if chat_member.status not in {"member", "administrator", "creator"}:
        await message.answer(AD_MSG_WITHDRAW, 
                             reply_markup=user_keyboards.get_withdraw_kb()) 
        return

    
    balance = await UsersDatabase.get_value(user_id,'balance')
    if balance < 250.0:
        await message.answer(text =f'''El saldo mínimo para retirar es  <b>250 Sol</b>
Su saldo: <b>{balance} Sol</b>
Lamentablemente, este límite tuvo que fijarse para no sobrecargar el sistema con retiradas de pequeñas cantidades.''',parse_mode="HTML", reply_markup=user_keyboards.get_check_balance_kb())
    else:
        await state.set_state(Form.card_number)
        await message.answer(text=f"💳 Envíame los datos de tu cuenta <b>%PAYMENTOS%</b> de la que deseas retirar tus saldos",parse_mode="HTML")

#Обработчик для кнопки "Зарабоать еще больше"
@router.message(F.text == "💰 Ganar aún más dinero 💰")
async def earn_more(message:Message, is_clb=False,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    bot_username = await get_bot_username(bot)
    await message.answer(f"""Nuestro proyecto es nuevo en telegram y necesitamos que todo el mundo nos conozca, por lo que estamos dispuestos a pagar por la publicidad 💵
 
🏆 Esta es tu link de enlace para las invitaciones 👇
 
<code>t.me/{bot_username}?start={user_id}</code>
 
✅ Copia el enlace y envíalo a tus amigos y conocidos
 
🏆 Por cada persona que visite el bot a través de tu enlace, obtienes <b>5 Sol</b>
 
Si alguien a quien invitas invita a nuevas personas, te pagan por usuario <b>2.5 Sol</b> 
 
Así que puedes ganar sin límites!""",parse_mode="HTML")



# Обработчик для вызова видео 
@router.callback_query(lambda c: c.data == "watch")
async def watch(clb: CallbackQuery, is_clb=True, include_earn_more = False,**kwargs):
    user_id = clb.message.chat.id 

    # Получаем текущую очередь пользователя
    queue = await UsersDatabase.get_value(user_id, "queue")
    video = await VideosDatabase.get_video_by_queue(queue)

    if video != -1:
        file_id = video[1]

        duration = int(video[2] * 0.75) #Позволяем скипать видео на 75%
        await clb.message.answer_video(video=file_id , reply_markup=user_keyboards.get_watch_kb(include_earn_more))
        await UsersDatabase.update_watching(user_id, duration, queue+1)  
    else:
        queue = 1  # Сбрасываем очередь
        video = await VideosDatabase.get_video_by_queue(queue)
        file_id = video[1]
        duration = int(video[2])
        await clb.message.answer_video(video=file_id, reply_markup=user_keyboards.get_watch_kb(include_earn_more))
        await UsersDatabase.update_watching(user_id, duration, 2)  # Сразу ставим 2, чтобы не повторялось первое видео
    await clb.answer()


# Обработчик для инлайн кнопки "Получить награду" 
@router.callback_query(lambda c: c.data == "receive")
async def receive(clb: CallbackQuery, is_clb=True,**kwargs):
    user_id = clb.message.chat.id if is_clb else clb.message.from_user.id
 
    update_limit= datetime.strptime(await UsersDatabase.get_value(user_id,'update_limit'), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    time_now= datetime.now(timezone.utc)
    if update_limit < time_now and update_limit !=0:
        await UsersDatabase.set_value(user_id,'today_left',20)
        
    user = await  UsersDatabase.get_user(user_id)
    watching = datetime.strptime(user[2], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    balance = user[3]
    update_limit= datetime.strptime(user[9], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    today_left = user[8]
    hold =  60*60*8
    if today_left>0:
        if watching < time_now:
            #Если начал смотреть, то рефреш времени будет через 8 часов.
            await UsersDatabase.reward_user(user_id,2.5,hold,today_left)

            await bot.send_message(user_id, f"""🎉 Has ganado <b>2.5 Sol</b> por ver el vídeo.\n                    
🤑 Su saldo: <b>{balance+2.5} Sol</b>""",parse_mode="HTML")
            await bot.delete_message(clb.message.chat.id,clb.message.message_id)
        else:
            await bot.answer_callback_query(clb.id,"""⚠️Tienes que ver el vídeo en su totalidad⚠️""")
            await bot.delete_message(clb.message.chat.id,clb.message.message_id)
            #Следующее видео вызывается отдельной функцией, а не предыдущей, для добавления инлайн кнопки мануала
        await watch(clb, is_clb =False, include_earn_more = True)
    else:
        time_left = await time_view(update_limit=update_limit,time_now=time_now)
        await bot.send_message(user_id, text=f'''⚠️ Hoy has cumplido con todos tus compromisos publicitarios y has recibido un premio! 😌

Puedes conseguir un nuevo contrato de publicidad durante: <b>{time_left}</b>

Si quieres ganar más, haz clic en el botón de abajo 👇''', parse_mode="HTML", reply_markup=user_keyboards.get_receive_kb()) 
        await bot.delete_message(clb.message.chat.id,clb.message.message_id)


@router.message(Command("set_admin"))
@is_admin
async def set_admin(message: Message, command: CommandObject, is_clb=False, **kwargs):
    if not command.args:
        await message.answer("❌ Empty request. \nExample: `/set_admin durov`\n!Username must be registered here!")
        return

    username = command.args.strip()
    user = await UsersDatabase.get_user_by_username(username)

    if user == -1:
        msg = f"❌ {username} not registered or username is not displayed."
        await message.answer(msg)
        logger.error(msg)
    else:
        await UsersDatabase.set_value(user[0], 'is_admin', 1)

        msg = f"✅ {username} is admin now 😎😎😎"
        await message.answer(msg)
        logger.success(msg)

@router.message(Command("admin"))
@is_admin
async def admin(message: Message, is_clb=False,**kwargs):

    user_id = message.chat.id
    
    await bot.send_message(user_id,"""📌Admin Panel📌:

/ad - Рассылка                            
/all_videos 
/set_admin - Назначение админа (/set_admin durov)        
/stats
/start - swith to user panel
                           
<a href="https://github.com/adoubt/earnbot2">github</a>
<a href="https://github.com/users/adoubt/projects/7/views/1">project board</a>""",link_preview_options=LinkPreviewOptions(is_disabled=True),parse_mode='HTML',reply_markup=user_keyboards.get_admin_kb())


@router.message(Command("ad"))
@is_admin
async def ad(message: Message, is_clb=False,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    state = await ConfigDatabase.get_value('ad_state')
    text=f"""<b>📢 Реклама</b>  

Перешли макет боту — он отправит его в • текущем режиме • 
 <b>all</b> — всем  
 <b>test</b> — только тебе  
 <b>admins</b> — админам  
 <b>off</b> — бот не реагирует (нужно для загрузки видео)  

*Несколько файлов сразу пока не поддерживается.*  

📊 <a href="{LOG_CHANNEL_LINK}">Логи отправки</a>"""
    ikb = user_keyboards.get_ad_kb(state)
    if is_clb:
        await message.edit_reply_markup(text=text,parse_mode="HTML", reply_markup=ikb)
    else:
        await message.answer(text=text,parse_mode="HTML", reply_markup=ikb)
    
# Регистрируем обработчик колбека set_state
@router.callback_query(lambda clb: clb.data.startswith('set_state'))
async def set_state_callback_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    state = data[2]
    await ConfigDatabase.set_value('ad_state',state)
    await ad(clb.message, is_clb= True)
    
@router.message(Command("stats"))
@is_admin
async def stats(message: Message, is_clb=False,**kwargs):
    total_count = await UsersDatabase.get_count()
    await message.answer(f"Registred users: {total_count}")

@router.message(Command("all_videos"))
@is_admin
async def all_videos(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    user_id = message.chat.id
    LIMIT_FOR_PAGE = 10
    total_videos = await VideosDatabase.get_count()
    if total_videos == 0:
        await message.answer('Nothing uploaded yet')
        return
    total_pages = (total_videos //LIMIT_FOR_PAGE) + 1
    if current_page >= total_pages:
        current_page = total_pages
    if current_page < 0:
        current_page = 0   
    videos = await VideosDatabase.get_all_offset(current_page*LIMIT_FOR_PAGE,LIMIT_FOR_PAGE)
    text = f'All Videos ({total_videos}):'
    ikb = user_keyboards.get_all_videos_kb(videos, current_page, total_pages)
    if is_clb:
        await message.edit_text(text=text, reply_markup=ikb)
    else:
        await message.answer(text=text, reply_markup=ikb) 
    

@router.callback_query(lambda clb: clb.data.startswith('all_videos'))
async def all_videos_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    current_page = int(data[2])
    await all_videos(clb.message, is_clb=True,current_page = current_page)    
   
@router.callback_query(lambda clb: clb.data.startswith('video_'))
async def video_clb_handler(clb: CallbackQuery,is_clb=False, **kwargs):
  
    data = clb.data.split('_',1)
    video_id = int(data[1])  
    file_id = await VideosDatabase.get_value(video_id,'file_id')
    await clb.message.answer_video(file_id, reply_markup=user_keyboards.get_admin_video_kb(video_id))
    await clb.answer()

@router.callback_query(lambda clb: clb.data == 'hide_file')
async def hide_file_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await clb.message.delete()

@router.callback_query(lambda clb: clb.data.startswith('delvideo'))
async def delvideo_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    video_id = int(data[1])  

    await VideosDatabase.del_video(video_id)
    logger.info(f'Deteted video_id: {video_id}')
    await clb.message.delete()


#Добавление видиков. стоит вконце чтобы не попадать под рекламные посты
@router.message(AdStateFilter("off"), F.video)
@is_admin
async def new_video(message: Message, is_clb=False, **kwargs):
    
    r = await VideosDatabase.create_video(file_id=message.video.file_id,
                                      file_name=message.video.file_name,
                                      duration=message.video.duration,
                                      queue=0)
    if not r:
        await message.reply("already exists")
        return
    await message.reply("👍🏿 Video successfully added!")
    logger.success('👍🏿 Video successfully added!')
 
#Рекланые посты 
@router.message(~AdStateFilter("off"), lambda msg: msg.forward_origin)
@is_admin
async def forward_handler(message: Message, is_clb=False, **kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    
    if message:
        asyncio.create_task(handle_send_ad(message, user_id))


# Обработчик команды или кнопки "exit"
@router.callback_query(lambda c: c.data == "exit")
async def exit_state(clb: CallbackQuery, state: FSMContext):

    await state.clear()  # Завершение текущего состояния
    await clb.message.answer(text='no olvides aplicar')
    await clb.message.delete()

# Обработчик для вызова обработчика "Заработать еще больше"
@router.callback_query(lambda c: c.data == "earn_more")
async def clb_withdraw(clb: CallbackQuery):
    
    await bot.answer_callback_query(clb.id)
    await earn_more(clb.message, is_clb = True)

@router.callback_query(lambda c: c.data == "verify_member")
async def verify_member(clb: CallbackQuery,state: FSMContext):
    user_id = clb.message.chat.id
    chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

    if chat_member.status == "member" or chat_member.status == "administrator" or chat_member.status == "creator":
        await clb.message.answer(text ='''Te has suscrito con éxito al canal ✅.
No es necesario que se dé de baja del canal si quiere retirar dinero.''')
        await UsersDatabase.set_value(user_id,'is_member',1)
        await withdraw(clb.message,state)
    else:
        await clb.message.delete()
        await clb.message.answer(text="Todavía no estás suscrito al canal",reply_markup=user_keyboards.get_withdraw_kb())
    await clb.answer()


# Определение состояний
class Form(StatesGroup):
    card_number = State()  # Состояние сбора номера карты
    email = State()  # Состояние сбора адреса почты
    amount = State()  # Состояние сбора суммы денег

# Обработка сообщений в состоянии card_number)
@router.message(Form.card_number)
async def process_card_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    card_number = message.text
    await UsersDatabase.set_value(user_id,'card_number',card_number)
    await state.set_state(Form.email)
    await message.answer(text=f'''Introduzca su dirección de correo electrónico y le enviaremos la información.
por ejemplo: <a href="amigobro@gmail.com">amigobro@gmail.com</a>''', parse_mode="HTML")

# Обработка сообщений в состоянии email)
@router.message(Form.email)
async def process_email(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = message.text
    email = is_valid_email(data)
    if not email:
        await message.answer(text=f'''Introduzca su dirección de correo electrónico y le enviaremos la información.
por ejemplo: <a href="amigobro@gmail.com">amigobro@gmail.com</a>''', parse_mode="HTML", reply_markup=user_keyboards.get_process_kb())
        return
    
    await UsersDatabase.set_value(user_id,'email',data)
    await state.set_state(Form.amount) 
    balance = await UsersDatabase.get_value(user_id,'balance')
    await message.answer(text=f'''Introduzca el importe que desea retirar.

El importe mínimo de retirada es <b>250 Sol</b>.

💵 Su saldo <b>%CURRENCIA% {balance}</b>''', parse_mode="HTML")

# Обработка сообщений в состоянии amount)
@router.message(Form.amount)
async def process_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = message.text
    balance = await UsersDatabase.get_value(user_id,'balance')
    ikb = user_keyboards.get_process_kb()
    try:
        currency = int(float(data))
        if  currency< 250 or currency>balance:
            await message.answer(text=f'''❌  No hay fondos suficientes en su saldo.El importe mínimo de retirada es <b>250 Sol</b>.
    
    💵 Your balance <b>%CURRENCY% {balance}</b>''',parse_mode="HTML",reply_markup=ikb)
            return
    except: #обработчик исключения если строка не является числом.
        await message.answer(text=f'''❌  Ingrese solo números.El importe mínimo de retirada es <b>250 Sol</b>.

💵 Your balance <b>%CURRENCY% {balance}</b>''',parse_mode="HTML",reply_markup=ikb)
        return
    await UsersDatabase.request(user_id = user_id,amount_requested = int(data))
  
         ###СМЕНА КЛАВЫ
    await message.answer( text=f'''Con éxito ✅ 
Su solicitud ha sido enviada ✅ 
Espere 48 horas para una respuesta''',reply_markup=user_keyboards.get_start_kb(requested=1))
       
    await state.clear()