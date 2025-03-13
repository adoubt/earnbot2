from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Any
from src.misc import CHANNEL_LINK,WATCHED_VIDEOS_THRESHOLD


def get_subscription_kb(link) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🗝 Подписаться', url=link)],
        [InlineKeyboardButton(text='🔎 Проверить подписку', callback_data="check_subscribe")]
    ])

    return ikb


def get_start_kb(requested:int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='Ver vídeos y ganar dinero 📺')],
        [KeyboardButton(text='Reglas 🎯')],
        [KeyboardButton(text='📱 Mi perfil'), KeyboardButton(text='Retirada de dinero  🏧')],
        [KeyboardButton(text='💰 Ganar aún más dinero 💰')]
    ]
    
    if requested == 1:
        buttons[1].append(KeyboardButton(text='Canal'))  # Добавляем кнопку "Канал" в строку с "Reglas 🎯"
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='/ad')],
        [KeyboardButton(text='/set_admin'), KeyboardButton(text='/stats')],
        [KeyboardButton(text='/all_videos'), KeyboardButton(text='/start')]    
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_ad_kb(state: str) -> InlineKeyboardMarkup:
    states = ["off", "all", "test", "admins"]

    keyboard = [
        [InlineKeyboardButton(text = f"{s}" if state != s else f"• {s} •", callback_data=f"set_state_{s}")]
        for s in states
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_all_videos_kb(videos,current_page:int, total_pages:int)-> InlineKeyboardMarkup:
   
    buttons = []
    for video in videos:
        video_id, file_id,file_name = video[0],video[1],video[3]
        
        buttons = buttons+[InlineKeyboardButton(text=file_name if file_name else str(video_id), callback_data=f"video_{video_id}")]
    pagination = []
    
    pagination.append(InlineKeyboardButton(text='<', callback_data=f"all_videos_{current_page-1}"))
    pagination.append(InlineKeyboardButton(text = f"{current_page+1}/{total_pages}", callback_data="current_page"))

    pagination.append(InlineKeyboardButton(text='>', callback_data=f"all_videos_{current_page+1}"))
    
    if total_pages>1:
        rows=  [[btn] for btn in buttons] + [pagination] 
    else: rows=  [[btn] for btn in buttons] 
    
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb

def get_admin_video_kb(video_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скрыть", callback_data="hide_file")],
        [InlineKeyboardButton(text="Удалить", callback_data=f"delvideo_{video_id}")]])
    return ikb

def get_watch_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Empezar a ver 📺", callback_data="watch")]])
    return ikb



def get_channel_kb(link:str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Canal',url=link)]])
    return ikb

def get_withdraw_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Únase al canal", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="comprobar las incripciones", callback_data="verify_member")]
        ])
    return ikb

# def get_choose_licenses_kb(
#     user_id, product_id, licenses, disabled, feature: int = None, in_cart: int = None
# ) -> InlineKeyboardMarkup:
#     buttons = []

#     # Логика определения выбранной лицензии (selected_license)
#     # Если в корзине есть товар, то он считается выбранным. Если нет, берем рекомендованную.

#     for license in licenses:
#         license_id=license[0]
#         if license_id not in disabled:
#             # Формируем текст кнопки с ценой
#             price = license[4]
#             price = int(price) if price.is_integer() else price
#             text = f"{license[2]} ${price}"
#             callback_data = f"addToCart:product_id={product_id}&license_id={license_id}&user_id={user_id}"
#             if license_id == in_cart:
#                 text = f'🛒 View in Cart ›'
#                 callback_data = "cart"
#             # Добавляем звезду для рекомендованной лицензии
#             if license_id == feature and license_id != in_cart:
#                 text += " 🔹"
            
#             # Меняем текст для активной выбранной лицензии
            
            
#             # Добавляем кнопку в список
#             buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

#     # Создаем footer с кнопками для навигации
#     footer = [
#         InlineKeyboardButton(text="‹ Back", callback_data=f"showcase_{product_id}")
#     ]

#     # Возвращаем разметку с кнопками
#     inline_keyboard = buttons + [footer]
#     return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

# def get_generated_cart_kb(cart_items, user_id, total_amount,payment_method) -> InlineKeyboardMarkup:

#     # Генерация кнопок для товаров
#     ikb = [
#         [
#             InlineKeyboardButton(text=item.get("name", "unknown item"), callback_data=f"showcase_{item.get('product_id', 'unknown')}"),
#             InlineKeyboardButton(text="🗑️", callback_data=f"delFromCart_{item.get('product_id', 'unknown')}_{item.get('license_id', 'unknown')}_{user_id}_cart")
#         ]
#         for item in cart_items
#     ]

#     # Кнопки действий
#     ikb += [
#         #[InlineKeyboardButton(text="🗑️ Remove All", callback_data=f"clear_cart_{user_id}")],
#         [InlineKeyboardButton(text=f"Method: {payment_method}", callback_data="choosePaymentMethod")],
#         [InlineKeyboardButton(text=f"💳 Checkout ${total_amount}", callback_data=f"checkout")]
#     ]

#     return InlineKeyboardMarkup(inline_keyboard=ikb)



# def get_main_seller_kb() -> ReplyKeyboardMarkup:
    
#     rkb = ReplyKeyboardMarkup(keyboard=[
#         #[KeyboardButton(text='🏠 Home',callback_data='homepage'),
#         [KeyboardButton(text='➕ New Beat')],
#         [KeyboardButton(text='📼 My Beats', callback_data='mybeats_0'),
#         KeyboardButton(text='📂 My Licenses')],
#         [KeyboardButton(text='⚙️ Settings', callback_data='settings_1'),
#          KeyboardButton(text='🌏 Buy Beats', callback_data='buyer')]],resize_keyboard=True
#     )
#     return rkb

# def get_link_kb(product_id:int,name:str=None)-> InlineKeyboardMarkup:
#     text = name if name else 'link'
#     url = LINK + str(product_id)
#     ikb = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=text, url=url)]
#     ]) 
#     return ikb


