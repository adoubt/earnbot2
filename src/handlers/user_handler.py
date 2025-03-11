import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command,StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.keyboards import user_keyboards

from src.methods.database.users_manager import UsersDatabase
from src.methods.database.videos_manager import VideosDatabase

router =  Router()

from src.misc import bot, SUPER_ADMIN
from src.handlers.decorators import new_user_handler

from src.methods.utils import parse_callback_data, is_valid_email

@router.message(Command("start"))
@new_user_handler
async def start_handler(message: Message, is_clb=False, product_id:int| None=None,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    wishlist_count = await WishlistsDatabase.get_wishlist_count(user_id)
    cart_count = await shopping_cart_service.count_items_in_cart(user_id)
    if not is_clb:
       
        text = 'Buy, sell, store beats on Syren with cryptocurrency whenever you want. <a href="https://t.me/CryptoBotEN/13">Learn more ></a>\n\nJoin <a href="https://t.me/CryptoBotEN">our channel</a> and <a href="https://t.me/CryptoBotEnglish">our chat</a>.'
        await message.answer(text=text,parse_mode="HTML",disable_web_page_preview=True, reply_markup = user_keyboards.get_main_buyer_kb(wishlist_count,cart_count))
    
        
    connector = get_connector(user_id)
    connected = await connector.restore_connection()
    try:
        if message.text != "/start" and message.text!="🌏 Buy Beats":
            if product_id is None:
                data = message.text.split(" ",1)[-1]
                product_id = int(data)
            product = await ProductsDatabase.get_product(product_id)
            if product == -1:
                await message.answer('Eror 404: no such a beat')

            # license_type=5
            # stems_link = product[7]
            # wav_link = product[6]
            preview_link = product[4] if product[4] !='' else product[5]

            # if stems_link =='':
            #     license_type=2
            # if wav_link !='':
            #     license_type=1
            # if mp3_link !='':
            #     license_type=0
           
            image_link = product[8]
            is_sold = product[9]
            collab = product[11]
            tags = product[12]
            seller = product[1]
            price = await LicensesDatabase.get_feature_by_user(seller)
            if price == -1:
                price = await LicensesDatabase.get_min_price_by_user(seller)
            channel = await UsersDatabase.get_value(seller,"channel")
            if preview_link == -1:
                await message.answer("404..")
            else:
                already_in_wishlist =  await WishlistsDatabase.is_product_in_wishlist(user_id,product_id)
                already_in_cart = True if await shopping_cart_service.check_item_in_cart(user_id,product_id) else False
                ikb = user_keyboards.get_showcase_kb(product_id=product_id,
                                                    price=price,
                                                    is_sold=is_sold,
                                                    channel=channel,
                                                    already_in_wishlist=already_in_wishlist,
                                                    already_in_cart=already_in_cart,
                                                    user_id=user_id)
                
                caption = 'SOLD' if is_sold else '' 
                if message.audio:
                    await message.edit_caption( reply_markup=ikb, caption =caption)
                else:
                    
                    await message.answer_audio(audio=preview_link, reply_markup=ikb , caption = caption)
    except Exception as e:
        print(e) 
        await message.answer('Wassap?', reply_markup = user_keyboards.get_main_buyer_kb(wishlist_count,cart_count) )            
   
    # if start_photo =="":
    #     await message.answer(text = text, parse_mode="HTML")
    # else:
    #     await message.answer_photo(photo =start_photo,caption=text,parse_mode="HTML" )


@router.callback_query(lambda clb: clb.data.startswith("showcase"))
@new_user_handler
async def showcase_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    product_id = data[1]
    await start_handler(clb.message, is_clb=True,product_id = product_id)


@router.message(F.text == "⚙️ Settings")
@new_user_handler
async def settings_handler(message: Message, is_clb=False, **kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id

    await message.answer(text = f'Settings',reply_markup = user_keyboards.get_settings_kb())

@router.message(F.text == "🌏 Sell Beats")
async def seller_handler(message: Message, is_clb=False, **kwargs):
    await message.answer(text='Seller Welcome MSG', reply_markup=user_keyboards.get_main_seller_kb())

@router.message(F.text == "🌏 Buy Beats")
async def buyer_handler(message: Message, is_clb=False, **kwargs):
    await start_handler(message)

@router.message(F.text.startswith("🤍 Wishlist"))
@new_user_handler
async def wishlist_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    if await WishlistsDatabase.get_wishlist_count(user_id)==0:
        
        await message.answer(text = "Wishlist is Empty")
        return

    wishlist = await WishlistsDatabase.get_wishlist_by_user(user_id)

    for item in wishlist:
        product_id = item[2]
        product = await ProductsDatabase.get_product(product_id)
        if product == -1: 
            await WishlistsDatabase.del_product_from_wishlists(product_id)
            await message.answer(text = "Please open Wishlist again")
            return
        #Лишний раз лезу в бд
        
        preview_link = product[4] if product[4] !='' else product[5]
        await message.answer_audio(audio=preview_link, reply_markup=user_keyboards.get_item_in_wishlist_kb(user_id,product_id))

@router.callback_query(lambda clb: clb.data == 'wishlist')
@new_user_handler
async def wishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await wishlist_handler(clb.message, is_clb=True)


@router.message(F.text.startswith("🛒 Cart"))
@new_user_handler
async def generate_cart_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id

    # Получаем товары из корзины
    cart_items = await shopping_cart_service.get_cart_items(user_id)
    await ProcessService.validate_order(user_id)
    # Если корзина пуста
    if not cart_items:
        await message.answer(text="Cart is Empty")
        return
    # Асинхронно получаем продукты и лицензии
    product_tasks = [ ProductsDatabase.get_product(product_id=item.product_id) for item in cart_items ] 
    license_tasks = [ LicensesDatabase.get_license(license_id=item.license_id) for item in cart_items ]
    # Ждем завершения всех запросов 
    products_results = await asyncio.gather(*product_tasks) 
    licenses_results = await asyncio.gather(*license_tasks) 
    total_amount = 0 
    enriched_cart = [] 
    # Собираем данные для корзины 
    for item, product, license in zip(cart_items, products_results, licenses_results): 
        if product ==-1:
            await shopping_cart_service.remove_item(user_id=user_id,product_id=item.product_id)
            await message.answer(text=f"Sorry 1 item from your cart has been deleted by seller")
            continue  # Пропускаем поврежденный товар
        # Если продукт или лицензия не найдены, пропускаем товар
        elif product[9] == 1:
            await shopping_cart_service.remove_item(user_id=user_id,product_id=product[0])
            await message.answer(text=f"Sorry, the beat from your cart was sold exclusively",reply_markup=user_keyboards.get_link_kb(product[0],product[2]))
        elif not license:
            # await shopping_cart_service.remove_item(user_id,product[0])
            await message.answer(text=f"Sorry, the license for '{product[2]}' has been changed.",)
            await shopping_cart_service.remove_item(user_id=user_id,product_id=product[0])
            # Возможно, здесь можно удалить товар из базы данных или корзины
            continue  # Пропускаем поврежденный товар


        total_amount += license[4] # Цена товара 
        enriched_cart.append({ 
            "item_id": item.item_id, 
            "cart_id": item.cart_id, 
            "product_id": item.product_id, 
            "quantity": item.quantity, 
            "license_id": item.license_id,
            "added_at": item.added_at, 
            "name": product[2], # Имя товара 
            "price": license[4], # Цена товара
                })
    if not enriched_cart :
        await message.answer(text="Cart is Empty")
        return
    text = await ProcessService.generate_cart_summary(enriched_cart)
    default_payment_method = await UsersDatabase.get_value(user_id,"default_payment_method")
    # Генерация клавиатуры с товарами
    keyboard = user_keyboards.get_generated_cart_kb(enriched_cart, user_id, total_amount,payment_method=default_payment_method)
    
    # Отправляем сообщение с корзиной и клавиатурой
    if message.text and message.from_user.is_bot:
        await message.edit_text(text=text,parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer(text=text,parse_mode='HTML', reply_markup=keyboard)
        if message.caption:
            await message.edit_caption(
                caption=None,
                reply_markup=None,  # Удалить клавиатуру
                remove_unset=True   # Указать, что отсутствующие поля нужно удалить
                )

        


@router.callback_query(lambda clb: clb.data == 'cart')
@new_user_handler
async def cart_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await generate_cart_handler(clb.message, is_clb=True)       

@router.message(F.text.startswith("🤝 Offers"))
@new_user_handler
async def offers_handler(message: Message, is_clb=False,**kwargs):
    await message.answer(text="This feature is not available yet.", show_alert=True)

@router.message(F.text.startswith("🛍 Purchases"))
@new_user_handler
async def offers_handler(message: Message, is_clb=False,**kwargs):
    await message.answer(text="This feature is not available yet.", show_alert=True)

@router.message(F.text == "📼 My Beats")
@new_user_handler
async def mybeats_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    total_beats = await ProductsDatabase.get_count_by_user(user_id)
    if total_beats == 0:
        await message.answer('Nothing uploaded yet, go to ➕ New Beat')
        return
    total_pages = (total_beats //10) + 1
    if current_page >= total_pages:
        current_page = total_pages
    if current_page < 0:
        current_page = 0
    
    beats = await ProductsDatabase.get_all_by_user(user_id, current_page*10)
    if is_clb:
        await message.edit_text(text=f'My Beats ({total_beats}):', reply_markup=user_keyboards.get_my_beats_kb(beats, current_page,total_pages))
    else:
        await message.answer(text=f'My Beats ({total_beats}):', reply_markup=user_keyboards.get_my_beats_kb(beats, current_page,total_pages))

@router.message(F.text == "📂 My Licenses")
@new_user_handler
async def mylicenses_handler(message: Message, is_clb=False, **kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    licenses = await LicensesDatabase.get_licenses_by_user(user_id=user_id, active_only=0)

    text = "Licenses:"
    keyboard = user_keyboards.get_licenses_kb(licenses)

    if is_clb:
        await message.edit_text(text=text, reply_markup=keyboard)
    else:
        await message.answer(text=text, reply_markup=keyboard)


@router.callback_query(lambda clb: clb.data == 'mylicenses')
@new_user_handler
async def mylicenses_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await mylicenses_handler(clb.message, is_clb=True)

@router.callback_query(lambda clb: clb.data == 'start')
@new_user_handler
async def start_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await start_handler(clb.message, is_clb=True)


@router.callback_query(lambda clb: clb.data == 'settings')
@new_user_handler
async def settings_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await settings_handler(clb.message, is_clb=True)

    


@router.callback_query(lambda clb: clb.data.startswith("showcase"))
@new_user_handler
async def showcase_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    product_id = data[1]
    await clb.answer()
    await start_handler(clb.message, is_clb=True,product_id = product_id)
    

@router.callback_query(lambda clb: clb.data.startswith("chooseLicense:"))
async def chooseLicense_clb_handler(clb: CallbackQuery, is_clb=True, data:str|None = None, **kwargs):
    
    user_id = clb.from_user.id
    parsed_data = parse_callback_data(clb.data)
    
    product_id = int(parsed_data.get('product_id')) if parsed_data.get('product_id') else None
    in_cart = int(parsed_data.get('in_cart')) if parsed_data.get('in_cart') else None


    cartItem = await shopping_cart_service.check_item_in_cart(user_id=user_id,product_id=product_id)
    in_cart = cartItem[0][4] if cartItem else None
    
    product = await ProductsDatabase.get_product(product_id)
    license_type=3
    seller = product[1]
    stems_link = product[7]
    wav_link = product[6]
    mp3_link = product[5]
    if stems_link =='':
        license_type=2
    if wav_link =='':
        license_type=1
    if mp3_link =='':
        license_type=0
    licenses = await LicensesDatabase.get_licenses_by_user(seller, license_type)

    disabled = await LicensesProductsDatabase.get_disabled(product_id)
    feature = next((license[0] for license in licenses if license[5] == 1), None)
    caption = '<b>Choose license:</b>'
    featured_text = ''
    for license in licenses: 
        if license[0] == in_cart:
            price = license[4]
            price = int(price) if price.is_integer() else price
            if license[5] == feature:
                featured_text ='🔹featured'
            caption = f"<b>{license[2]}\n(in cart)\n\nInclude: {license[3]}\nTotal: ${price}</b>"
    
   
    await clb.message.edit_caption(caption = caption, parse_mode='HTML',reply_markup = user_keyboards.get_choose_licenses_kb(
        user_id=user_id,product_id=product_id,licenses=licenses,disabled=disabled,feature=feature,in_cart=in_cart))


@router.callback_query(lambda clb: clb.data.startswith("addTowishlist"))
async def addTowishlist_clb_handler(clb: CallbackQuery, is_clb=True, **kwargs):
    user_id = clb.from_user.id
    data = clb.data.split('_',1)
    product_id, = data[1]
    #product = await ProductsDatabase.get_product(product_id)
    await WishlistsDatabase.add_to_wishlist(user_id,product_id)
    # already_in_cart = 1 if await shopping_cart_service.check_item_in_cart(user_id,product_id) else 0
    # seller, is_sold= product[1],product[9]
    # channel = await UsersDatabase.get_value(seller,'channel')
    await start_handler(clb.message,is_clb=True,product_id=product_id)
    #await clb.message.edit_reply_markup(reply_markup = user_keyboards.get_showcase_kb(product_id=product_id,is_sold=is_sold,channel=channel,already_in_wishlist=1,already_in_cart=already_in_cart,price = ))


@router.callback_query(lambda clb: clb.data.startswith("delFromWishlist"))
async def delFromWishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',3)
    user_id,product_id,action = data[1],data[2],data[3]
    await WishlistsDatabase.del_from_wishlist(user_id,product_id)
    if action == 'del':
        await clb.message.delete()
        if await WishlistsDatabase.get_wishlist_count(user_id)==0:
        
                await bot.send_message(chat_id=user_id,text = "Wishlist is Empty")
        return
    elif action == 'refresh':
        await start_handler(clb.message,is_clb=True,product_id=product_id)




@router.callback_query(lambda clb: clb.data.startswith('mybeats'))
@new_user_handler
async def mybeats_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    current_page = int(data[1])
    await mybeats_handler(clb.message, is_clb=True,current_page = current_page)

@router.callback_query(lambda clb: clb.data.startswith('licenses'))
@new_user_handler
async def licenses_clb_handler(clb: CallbackQuery,state = FSMContext, product_id:int|None = None, is_clb=False, **kwargs):
    if product_id == None:
        data = clb.data.split('_',1)
        product_id = int(data[1])
    product = await ProductsDatabase.get_product(product_id)
    license_type=3
    seller = product[1]
    stems_link = product[7]
    wav_link = product[6]
    mp3_link = product[5]
    if stems_link =='':
        license_type=2
    if wav_link =='':
        license_type=1
    if mp3_link =='':
        license_type=0
    
    licenses = await LicensesDatabase.get_licenses_by_user(seller, license_type)
    disabled = await LicensesProductsDatabase.get_disabled(product_id)
    await state.clear()
    if is_clb:
        await bot.edit_message_reply_markup(chat_id=clb.message.chat.id, message_id=clb.message.message_id,reply_markup = user_keyboards.get_product_licenses_kb(product_id, licenses,disabled))
    else:
        await clb.message.edit_text(text=f'Licenses:',reply_markup = user_keyboards.get_product_licenses_kb(product_id, licenses,disabled))   

@router.callback_query(lambda clb: clb.data.startswith('files'))
@new_user_handler
async def files_clb_handler(clb: CallbackQuery, state = FSMContext,is_clb=False, **kwargs):
    await state.clear()
    data = clb.data.split('_',1)
    product_id = int(data[1])
    product = await ProductsDatabase.get_product(product_id)
    preview_link,mp3_link,wav_link,stems_link = product[4],product[5],product[6],product[7]
    await clb.message.edit_text(text='Files:\n(tap to show)',reply_markup = user_keyboards.get_files_kb(product_id,preview_link,mp3_link,wav_link,stems_link))   

@router.callback_query(lambda clb: clb.data.startswith('showfile_'))
@new_user_handler
async def showfile_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    product_id = int(data[2])
    product = await ProductsDatabase.get_product(product_id)
    preview_link,mp3_link,wav_link,stems_link = product[4],product[5],product[6],product[7]
    if data[1] == 'mp3':
        await clb.message.answer_audio(audio = mp3_link,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'wav': 
        await clb.message.answer_document(document = wav_link,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'stems':
        await clb.message.answer_document(document = stems_link,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'preview':
        await clb.message.answer_audio(audio = preview_link,reply_markup =user_keyboards.get_hide_file_kb())  
    await clb.answer()



@router.callback_query(lambda clb: clb.data.startswith('deletefile_'))
@new_user_handler
async def deletefile_clb_handler(clb: CallbackQuery,state = FSMContext, is_clb=False, **kwargs):
    
    data = clb.data.split('_',2)
    product_id = int(data[2])
    file_type = data[1]
    await ProductsDatabase.set_value(product_id,f'{file_type}_link','')
    await state.clear()
    product = await ProductsDatabase.get_product(product_id)
    preview_link,mp3_link,wav_link,stems_link = product[4],product[5],product[6],product[7]
    await clb.message.edit_text(text='Files:\n(tap to show)',reply_markup = user_keyboards.get_files_kb(product_id,preview_link,mp3_link,wav_link,stems_link))

class EditFile(StatesGroup):
    file_ask = State()

@router.callback_query(lambda clb: clb.data.startswith('editfile_'))
@new_user_handler
async def editfile_clb_handler(clb: CallbackQuery, state = FSMContext, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    product_id = int(data[2])
    await state.set_data([product_id,data[1]])
    file_type = data[1]
    if file_type == 'mp3':
        text = 'Upload or forward .MP3'
    elif file_type == 'wav':
        text = 'Upload or forward .WAV'
    elif file_type == 'stems':
        text = 'Upload or forward .ZIP (or other archive)'
    elif file_type == 'preview':
        text = 'Upload or forward preview .MP3 '
    await state.set_state(EditFile.file_ask)
    
    await clb.message.edit_text(text=text,reply_markup =user_keyboards.get_edit_file_kb(product_id,file_type))



@router.message(EditFile.file_ask)
async def file_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    data = await state.get_data()
    product_id = data[0]
    file_type = data[1]

    link = get_file_id(message, file_type)

    if link:
        await ProductsDatabase.set_value(product_id, f'{file_type}_link', link)
        text = f'Updated!\nFiles:'
        
    else:
        text = f'Error: Unexpected file format, not {file_type}\nFiles:'
    product = await ProductsDatabase.get_product(product_id)
    preview_link,mp3_link,wav_link,stems_link = product[4],product[5],product[6],product[7]
    await state.clear()
    await message.answer(text=text, reply_markup = user_keyboards.get_files_kb(product_id,preview_link,mp3_link,wav_link,stems_link)) 
         

@router.callback_query(lambda clb: clb.data == 'hide_file')
async def hide_file_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await clb.message.delete()

@router.callback_query(lambda clb: clb.data.startswith('enable'))
async def enable_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',2)[1]
    license_id = clb.data.split('_',2)[2]
    await LicensesProductsDatabase.del_row(license_id,product_id)
    await licenses_clb_handler(clb, product_id,is_clb=True)

@router.callback_query(lambda clb: clb.data.startswith('disable'))
async def disable_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',2)[1]
    license_id = clb.data.split('_',2)[2]
    await LicensesProductsDatabase.create(product_id,license_id,1)
    await licenses_clb_handler(clb, product_id,is_clb=True)

@router.callback_query(lambda clb: clb.data.startswith('delproduct'))
async def delproduct_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',2)[2]
    is_sure = clb.data.split('_',2)[1]
    if is_sure =='0':
        await clb.message.edit_text(text = 'Are You Sure?', reply_markup=user_keyboards.get_delbeat_kb(product_id))
        return
    await ProductsDatabase.del_product(product_id)
    await clb.message.edit_text(text='Deleted')

@router.callback_query(lambda clb: clb.data.startswith('delproduct_sure_'))
async def del_sure_product_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',1)[1]
    await clb.message.edit_text(text = 'Are You Sure?', reply_markup=user_keyboards.get_delbeat_kb(product_id))

class EditProductNameState(StatesGroup):
    name_ask = State()

@router.callback_query(lambda clb: clb.data.startswith('editproductname'))
async def editproductname_handler(clb: CallbackQuery, state: FSMContext, is_clb=False, **kwargs):
    product_id = int(clb.data.split('_',2)[1])
    await state.set_state(EditProductNameState.name_ask)
    await state.set_data([product_id,clb])
    await clb.message.edit_text(text='Type New Name...', reply_markup=user_keyboards.get_editbeatname_kb(product_id))

@router.message(EditProductNameState.name_ask)
async def name_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    name = message.text
    data = await state.get_data() 
    product_id= data[0]
    clb = data[1]
    await ProductsDatabase.set_value(product_id,'name', name) 
    await state.clear()
    await message.delete()
    await beat_clb_handler(clb,product_id)
    # await beat_handler(product_id)



class NewBeatState(StatesGroup):
    mp3_ask = State()
    wav_ask = State()
    stems_ask = State()
    preview_ask = State()

@router.message(F.text =="➕ New Beat")
@new_user_handler
async def newbeat_handler(message: Message,state: FSMContext, is_clb=False,**kwargs):
    
    user_id = message.chat.id if is_clb else message.from_user.id
    total_beats = await ProductsDatabase.get_count_by_user(user_id)
    total_licenses = await LicensesDatabase.get_count_by_user(user_id)

    if total_beats == 0 and total_licenses == 0: await LicensesDatabase.set_default(user_id)
    await state.set_state(NewBeatState.mp3_ask)

    error_text = "Error: timed out. Please try again.\n\n" if is_clb else ''
    await message.answer(text= f'{error_text}Upload or forward .MP3', reply_markup = user_keyboards.get_cancel_kb())

@router.callback_query(lambda clb: clb.data.startswith('cancel'))
async def cancel_handler(clb: CallbackQuery,state = FSMContext, is_clb=False, **kwargs) -> None:
    
    parsed_data = parse_callback_data(clb.data)
    reffer = parsed_data.get('reffer') if parsed_data.get('reffer') else None
    params = parsed_data.get('params') if parsed_data.get('params') else None
    if reffer == 'mylicense':
        if params !='None':
            license_id= int(params)
            await mylicense_clb_handler(clb, license_id)

        else:
            await mylicenses_handler(clb.message, is_clb=True)
    # await bot.delete_message(chat_id=clb.message.chat.id,message_id=clb.message.message_id - 1)
    # await clb.message.delete()
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()



@router.message(NewBeatState.mp3_ask)
async def mp3_ask_callback_handler(message: types.Message, state= FSMContext, **kwargs):
    user_id = message.from_user.id
    if message.audio is None or message.document is None:
        
        await state.clear()
    performer = message.audio.performer
    title = message.audio.title
    name = message.audio.file_name
    mp3_link = message.audio.file_id

    #proverka etogo bita v magaze
    

    await state.set_state(NewBeatState.wav_ask)
    await state.set_data([user_id,performer,title,name,mp3_link])
    await message.answer(text= f'Upload or forward .WAV', reply_markup = user_keyboards.get_cancel_kb())

@router.message(NewBeatState.wav_ask)
async def wav_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    
    data = await state.get_data() 
    user_id = data[0]
    performer = data[1]
    title = data[1]
    name = data[3]
    mp3_link = data[4]
    wav_link = message.document.file_id
    
    await state.set_state(NewBeatState.stems_ask)
    await state.set_data([user_id,performer,title,name,mp3_link,wav_link])
    await message.answer(text= f'Upload or forward .ZIP',reply_markup = user_keyboards.get_newbeat_kb())

@router.callback_query(lambda clb: clb.data == 'skip_stems')
async def skip_stems_handler(clb: CallbackQuery, state : FSMContext, is_clb=False, **kwargs):
    await state.set_state(NewBeatState.stems_ask)
    await stems_ask_callback_handler(message = clb.message,state= state, is_skip=True,is_clb=True)
    await clb.answer()

@router.message(NewBeatState.stems_ask)
async def stems_ask_callback_handler(message: types.Message, state: FSMContext,is_clb=False, is_skip= False,**kwargs):
    
    data = await state.get_data() 
    if data == {}:
        await message.answer()
        await newbeat_handler(message,state,True)
        return
    user_id = data[0]
    performer = data[1]
    title = data[1]
    name = data[3]
    mp3_link = data[4]
    wav_link = data[5]
    await state.clear()
    if is_skip:
        await ProductsDatabase.create_product(user_id = user_id,name = name,mp3_link=mp3_link,wav_link=wav_link, preview_link=mp3_link, performer=performer,title = title)
    
    else:
        stems_link = message.document.file_id
        await ProductsDatabase.create_product(user_id = user_id,name = name,mp3_link=mp3_link,wav_link=wav_link,stems_link=stems_link, preview_link=mp3_link,performer=performer,title = title)
    
    logger.success(f"New product {name} by {user_id}")
    await message.answer(text= f'Created, go to 📼 My Beats')

@router.callback_query(lambda clb: clb.data.startswith('beat'))
async def beat_clb_handler(clb: CallbackQuery, product_id:int|None=None,is_clb=False, **kwargs):
    
    if product_id is None:
        data = clb.data.split('_',1)
        product_id = int(data[1])
    product = await ProductsDatabase.get_product(product_id) 
    link = f't.me/OctarynBot?start={product_id}'
    name = product[2]
    await clb.message.edit_text(text=f'<b>{name}</b>\n\n(tap to copy link):\n<code>{link}</code>',parse_mode="HTML",reply_markup=user_keyboards.get_beat_kb(product_id))


@router.callback_query(lambda clb: clb.data == 'setdefaultlicenses')
async def setdefaultlicenses_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    user_id = clb.message.chat.id
    await LicensesDatabase.set_default(user_id)
    await mylicenses_handler(clb.message, is_clb=True)
    await clb.answer()

class NewLicense(StatesGroup):
    file_ask = State()

@router.callback_query(lambda clb: clb.data == 'newlicense')
async def newlicense_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    user_id = clb.message.chat.id

    await LicensesDatabase.create_license(user_id)
    await mylicenses_handler(clb.message, is_clb=True)    

@router.callback_query(lambda clb: clb.data.startswith('mylicense_'))
async def mylicense_clb_handler(clb: CallbackQuery, license_id:int|None=None,is_clb=False, **kwargs):
    if license_id is None:
        data = clb.data.split('_',1)
        license_id = int(data[1])
    license = await LicensesDatabase.get_license(license_id) 
    is_archived,feature, is_active = license[10], license[5], license[12]
    meta_preview = ''
    if is_archived == 1:
        meta_preview += '🗃'
    if feature ==1:
        meta_preview += '🔹'
    if is_active !=1:
        meta_preview +='💤'
    user_id = clb.chat.id if is_clb else clb.message.chat.id 
    message_id = clb.message_id-1 if is_clb else clb.message.message_id # Если пришло с колбеком, значит условия перезаписаны и стоит удалить мусор из чата. зачем вернуться к лицухе
    
    if is_clb: 
        await bot.delete_messages(chat_id=user_id,message_ids={clb.message_id,clb.message_id-1})
        # await bot.delete_message(chat_id=user_id,message_id=clb.message_id) 
        await bot.send_message(chat_id=user_id,text=f'{meta_preview}<b>{license[2]}</b>',parse_mode="HTML",reply_markup=user_keyboards.get_mylicense_kb(license))
    else:
        await bot.edit_message_text(chat_id=user_id,message_id=message_id,text=f'{meta_preview}<b>{license[2]}</b>',parse_mode="HTML",reply_markup=user_keyboards.get_mylicense_kb(license))
    

class LicenseEdit(StatesGroup):
    name_ask = State()
    desc_ask = State()
    price_ask = State()
    upload_ask = State()
    any_state = State(state='*')

@router.callback_query(lambda clb: clb.data.startswith('licenseedit'))
async def licenseedit_clb_handler(clb: CallbackQuery,is_clb=False, state = FSMContext, **kwargs):
    
    user_id = clb.message.chat.id
    data = clb.data.split('_',3)
    license_id = data[2]
    
    if data[1] == 'name':
        await state.set_state(LicenseEdit.name_ask)
        await clb.message.edit_text(text = 'Imput new name',reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id))
    elif data[1] == 'desc':
        await state.set_state(LicenseEdit.desc_ask)
        await clb.message.edit_text(text = 'Imput new description',reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id))
    elif data[1] == 'type': 
        await LicensesDatabase.toggle_license_type(license_id)
    
        await mylicense_clb_handler(clb,license_id)
    
    elif data[1] == 'active':
        r = await LicensesDatabase.toggle_license_active(license_id)
        if r ==-1:
            await clb.message.edit_text(text = 'Error: Some fields are empty')
            
        else:
            await mylicense_clb_handler(clb,license_id)
    elif data[1] == 'price':
        await state.set_state(LicenseEdit.price_ask)
        await clb.message.edit_text(text = 'Imput new price',reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id))
        
    elif data[1] == 'feature':
        if data[3] == '1':
            await LicensesDatabase.set_featured_license(user_id, license_id)
        else:
            await LicensesDatabase.set_value(license_id,"feature",0)
        await mylicense_clb_handler(clb,license_id)

    elif data[1] == 'showfile':
        license= await LicensesDatabase.get_license(license_id)
        license_file_id = license[9]
        template_id = license[8]
        
        if license_file_id:
            await clb.message.answer_document(document = license_file_id,reply_markup =user_keyboards.get_hide_file_kb())
        
        elif template_id:
            markdown = await LicenseTemplates.get_markdown(seller_id=user_id)
            file_like_object = io.BytesIO(markdown.encode('utf-8'))
            file_like_object.seek(0)  # Переходим в начало файла
            await clb.message.answer_document(document=InputFile(file_like_object, filename="template_license.txt"),reply_markup=user_keyboards.get_hide_file_kb())
        else: #тут шерю дефолт
            markdown = FSInputFile("src/default_markdown.md", filename="default_template.md")
            await clb.message.answer_document(document=markdown,reply_markup=user_keyboards.get_hide_file_kb())
        await clb.answer()
    elif data[1] == 'uploadfile':
        await state.set_state(LicenseEdit.upload_ask)
        # await state.set_data([license_id])
        text ="""
Upload or forward yor contract file

The contract will be generated from <i>markdown_file.md</i> with variables like: <pre>
{CONTRACT_DATE}
{PRODUCER_ALIAS}
{PRODUCT_TITLE}
etc...</pre>
There are different templates on exclusive and non-exclusive. 
Non-exclusive template will be applied on all non-exclusive licenses. 
"""
        await clb.message.edit_text(text = text,parse_mode ='HTML',reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id))
    elif data[1] == 'delete':
        await LicensesDatabase.del_license(license_id) 
        
        await mylicenses_handler(clb.message, is_clb = True) 
        await state.clear()
    await state.set_data([license_id])

# Обработчик для состояний в LicenseEdit
@router.message(StateFilter(LicenseEdit))  # Фильтруем по группе состояний LicenseEdit
async def handle_license_edit(message: types.Message, state: FSMContext, **kwargs):
    # Получаем текущее состояние
    current_state = await state.get_state()
    data = await state.get_data() 
    license_id= data[0]
    if current_state == LicenseEdit.name_ask.state:
        if not message.text:
            await message.delete()
            await bot.edit_message_text(text = 'No text given, pls input again!', chat_id = message.chat.id,message_id=message.message_id-1,reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id))
            await state.set_state(LicenseEdit.name_ask)
            return        
        key = "name"
        new_value = message.text

    elif current_state == LicenseEdit.desc_ask.state:
        if not message.text:
            await message.delete()
            await bot.edit_message_text(text = 'No text given, pls input again!', chat_id = message.chat.id,message_id=message.message_id-1,reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id))
            await state.set_state(LicenseEdit.desc_ask)
            return
        key = "description"
        new_value = message.text
        
    elif current_state == LicenseEdit.price_ask.state:
        try:
            new_value = float(message.text.replace(",", "."))
            if new_value < 1:
                raise ValueError("Value must be at least 1")  # Искусственно выбрасываем исключение для обработки
        except (ValueError, TypeError):
            await message.delete()
            await bot.edit_message_text(
                text='Only numbers (min 1)', 
                chat_id=message.chat.id, 
                message_id=message.message_id - 1, 
                reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id)
            )
            await state.set_state(LicenseEdit.price_ask)
            return
        
        key = 'price'


    elif current_state == LicenseEdit.upload_ask.state:
        
        if not message.document:
            await message.delete()
            await bot.edit_message_text(text = 'Please send file as document..', chat_id = message.chat.id,message_id=message.message_id-1,reply_markup=user_keyboards.get_cancel_kb(reffer='mylicense',params=license_id)) 
            await state.set_state(LicenseEdit.upload_ask)
            return
        key = "license_file_id"
        new_value = message.document.file_id
        
        
    await LicensesDatabase.set_value(license_id,key,new_value)
    
    # await bot.edit_message_text(text = 'Updated!', chat_id = message.chat.id,message_id=message.message_id-1,reply_markup=user_keyboards.get_hide_file_kb()) 
    await mylicense_clb_handler(message,license_id, is_clb = True)

    await state.clear()


#Cart
@router.callback_query(lambda clb: clb.data.startswith('addToCart'))
async def addToCart_clb_handler(clb: CallbackQuery,is_clb=True, **kwargs):
    user_id = clb.message.chat.id
    parsed_data = parse_callback_data(clb.data)
    product_id = int(parsed_data.get('product_id')) if parsed_data.get('product_id') else None
    license_id = int(parsed_data.get('license_id')) if parsed_data.get('license_id') else None
    await shopping_cart_service.add_item(user_id,product_id,license_id)
    await chooseLicense_clb_handler(clb,is_clb=False,data = f'chooseLicense:product_id={product_id}&license_id={license_id}')

@router.callback_query(lambda clb: clb.data.startswith('delFromCart'))
async def delFromCart_clb_handler(clb: CallbackQuery,is_clb=True, **kwargs):
    user_id = clb.message.chat.id
    data = clb.data.split('_',4)
    product_id = int(data[1])
    await shopping_cart_service.remove_item(user_id,product_id)
    if data[4] =='license':
        await chooseLicense_clb_handler(clb,is_clb=False,data = f'chooseLicense:product_id={product_id}&license_id')
    else:
        await generate_cart_handler(clb.message,is_clb=True)



#Stars_payment
   
@router.callback_query(F.data == "paystarscancel")
async def on_paystars_cancel(callback: CallbackQuery, **kwargs):
    # await callback.answer(l10n.format_value("donate-cancel-payment"))

    await callback.message.delete()

@router.callback_query(lambda clb: clb.data.startswith('paystars'))
async def paystars_clb_handler(clb: CallbackQuery,is_clb=False,  **kwargs):
    
    user_id = clb.message.chat.id
    
    data = clb.data.split('_',3)
 
    product_id = int(data[1])
    license_id = int(data[2])

    amount = await LicensesDatabase.get_value('price',license_id)
    prices = [LabeledPrice(label="XTR", amount=amount)]


    await clb.message.answer_invoice(
    title='Invoice Title',
    description=f'You want to pay {amount} XTR(stars)',
    prices=prices,

    # provider_token оставляем пустым
    provider_token="",

    # тут передаем любые данные (пэйлоад)
    # например, идентификатор услуги которую покупает юзер
    # или уровень подписки
    # или еще что-то такое
    # мы же передадим кол-во. задоначенных звёзд (просто так)
    payload=f"paystars_{product_id}_{license_id}_{amount}",

    # XTR - это код валюты Telegram Stars
    currency="XTR",

    # не забываем передать нашу кастомную клавиатуру
    # напоминаю, что это можно не делать
    # ТГ сам добавит кнопку оплаты, если тут ничего не передавать
    reply_markup=user_keyboards.get_paystars_kb(amount)
    )

@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    # смысл on_pre_checkout_query такой же, как и в любых других платежах
    # бот должен ответить в течение 10 секунд
    # ..
    payload = query.invoice_payload
    data = payload.split('_',3)
    product_id = int(data[1])
    license_id = int(data[2])
    amount = int(data[3])
    
    
    # тут можно/нужно проверить доступность товара/услуги, прямо перед оплатой
    product = await ProductsDatabase.get_product(product_id)
    is_sold = product[9]
    
    license = LicensesDatabase.get_license(license_id)
    price = license[4]
    is_active = license[11]
    # добавить проверку наличия файлов
    # дорбавить проверку работы шлюза у битмаря и платформы?
    if is_sold == 1:
        await query.answer(
       ok=False,
       error_message="Unfortunately the beat just has been SOLD"
        )
    elif price != amount:
        await query.answer(
       ok=False,
       error_message="Sorry, the price just was changed"
        )
    elif is_active == 0:
        await query.answer(
       ok=False,
       error_message="Sorry this license was disabled, contact seller for more"
        )
    else :
        await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    # await bot.refund_star_payment(
    #     user_id=message.from_user.id,
    #     telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    # )

    customer_id = message.from_user.id
    payload = message.invoice_payload
    data = payload.split('_',3)
    invoice = message.telegram_payment_charge_id
    product_id = int(data[1])
    license_id = int(data[2])
    amount = message.total_amount #int(data[3])

    license = LicensesDatabase.get_license(license_id)
    license_type,license_file = license[6],license[8]

    product = ProductsDatabase.get_product(product_id)
    seller_id, mp3_link,wav_link, stems_link,collab= product[1],product[5],product[6],product[7],product[11]

    promo_code_id = None
    offer_id = None
    payment_method = 'STARS'
    discount = 0.00 # должно быть в payload
    total_amount = (amount * (100-SERVICE_FEE)) - discount
    
    currency = 'XTR'


    logger.success(f"Sale! Seller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}")
    #Формирую sale
    try:

        await SalesDatabase.create_sale(customer_id,
                                        seller_id,
                                        product_id,
                                        total_amount,
                                        currency,
                                        discount,
                                        SERVICE_FEE,
                                        license_file,
                                        promo_code_id,
                                        invoice,
                                        payment_method,
                                        offer_id)
    except Exception as e:
        await bot.send_message(chat_id =SUPER_ADMIN, text = f'Error while creating Sale after success payment. \nSeller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}\n{e}')
        logger.error(f'Error while creating Sale after success payment. \n Seller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}')
        await message.answer(text=f'Some problems, I got this msg and will fix ASAP!!!!! you can contact me btw @brokeway')
        await bot.send_message(chat_id = seller_id,text = f'Yo, we\'ve problems with the delivery of your files, fix it or send it manually (buyer contacts in the menu/sales)')
    #Отправляю товары
    try:
        # Базовый массив media с первым элементом, который будет всегда
        media = [InputMediaAudio(media=mp3_link, caption="Caption_mp3")]

        # Добавляем дополнительные элементы в зависимости от license_type
        if license_type in [2, 5, 4, 3]:
            media.append(InputMediaDocument(media=wav_link, caption="Caption_wav"))
        if license_type in [5, 4, 3]:
            media.append(InputMediaDocument(media=stems_link, caption="Caption_stems"))
        media.append(InputMediaDocument(media=license_file, caption="License_file"))
        # Отправляем медиа-группу
        await bot.send_media_group(chat_id=message.chat.id, media=media)
    except Exception as e:
        await bot.send_message(chat_id =SUPER_ADMIN, text = f'Files after success payment wasn\'t delivered. \nSeller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}\n{e}')
        logger.error(f'Files after success payment wasn\'t delivered. \n Seller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}')
    #Ставлю SOLD после продажи
    if license_type == 5:
        await ProductsDatabase.set_value(product_id,'is_sold',1)
    
    
    #Уведомляю продавца
    await bot.send_message(chat_id = seller_id, text =f'Congratulations! You’ve made a sale!')# тут будет клава к продаже поближе
    #приват канал для регистрации всех транзакций тут же




@router.callback_query(lambda clb: clb.data == 'choosePaymentMethod')
async def choosePaymentMethod_clb_handler(clb: CallbackQuery, **kwargs):
    user_id = clb.message.chat.id
    default_payment_method = await UsersDatabase.get_value(user_id, "default_payment_method")
    payment_methods = {
        "CryptoBot", "🚧 Ton","🚧 Stars"
    }
    await clb.message.edit_text(text = f"Default payment method:\n\n<b>{default_payment_method}</b>",
                                   parse_mode='HTML',
                                   reply_markup=user_keyboards.get_payment_methods_kb(default_payment_method,payment_methods ))

@router.callback_query(lambda clb: clb.data.startswith('setDefaultPaymentMethod'))
async def setDefaultPaymentMethod_clb_handler(clb: CallbackQuery,is_clb=True, **kwargs):
    user_id = clb.message.chat.id
    data = clb.data.split('_',1)
    method = data[1]
    # Проверка, начинается ли метод с 🚧
    if method.startswith("🚧"):
        # Отправка всплывающего сообщения (alert)
        await clb.answer(text="This feature is not available yet.", show_alert=True)
        return  # Прерываем дальнейшую обработку
    await UsersDatabase.set_value(user_id,"default_payment_method",method)
    await choosePaymentMethod_clb_handler(clb)

@router.message(F.text)
async def anytext_handler(message:Message,**kwargs):
    await start_handler(message,is_clb=True)


@router.callback_query(F.data == "emptycallback")
async def emptycallback(clb: CallbackQuery, **kwargs):
   await clb.answer()

@router.callback_query(lambda clb: clb.data == 'notifications')
async def notifications_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await clb.answer('This feature is not available yet.')



@router.callback_query(lambda clb: clb.data.startswith("checkout"))
async def checkout_clb_handler(clb: CallbackQuery, **kwargs):
    user_id = clb.message.chat.id
    
    sticker_id = "CAACAgIAAxkBAAEGZ9FkGvCRnhLZZIHCXv6JhGHREyzgkgACtRMAAp2w0UuLqpm8iw7ZOSoE"  # пример ID стикера
    message = await bot.send_sticker(user_id, sticker=sticker_id)
   
    ###### какая то проверка
    validation = await ProcessService.validate_order(user_id)
    if not validation["valid"]:
        await clb.message.answer("Ошибка:\n" + "\n".join(validation["errors"]))
        await generate_cart_handler(clb.message, is_clb=True)
        return
    enriched_cart = validation['enriched_cart']
    cart_total = validation['cart_total']
    cart_id, user_id, subtotal_amount, service_fee, total_amount,payment_method = cart_total.values()
    if payment_method == 'CryptoBot':
        # await clb.message.answer(text = "Ваш заказ корректен. Готов к оплате!",reply_markup=user_keyboards.get_order_summary_kb())
        invoice = await cp.create_invoice(total_amount, "USDT")
        print("invoice link:", invoice.bot_invoice_url)
        await message.answer(f"pay: {invoice.mini_app_invoice_url}")
        invoice.await_payment(message=clb.message)
        await orders_service.create_order(user_id=user_id,cart_id=cart_id,)
        
        await clb.message.answer(f'ссылка на оплату: {invoice.bot_invoice_url}')
    await bot.delete_message(user_id, message.message_id)



# # Обработчик создания счета
# @router.message()
# async def get_invoice(message):
#     invoice = await cp.create_invoice(1, "USDT")  # Создаем счет на 1 USDT
#     await message.answer(f"Pay here: {invoice.bot_invoice_url}")
#     invoice.await_payment(message=message)  # Ждем оплаты

# Обработчик успешной оплаты

@cp.polling_handler()
async def handle_payment(
    invoice: Invoice,
    message: Message,
) -> None:
    await message.answer(
        f"payment received: {invoice.amount} {invoice.asset}",
    )

@cp.expired_handler()
async def expired_invoice_handler(invoice: Invoice, payload: str):
    print(f"Expired invoice", invoice.invoice_id, payload) 
    