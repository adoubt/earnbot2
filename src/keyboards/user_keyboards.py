from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Any

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


