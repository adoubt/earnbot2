from src.methods.database.users_manager import UsersDatabase
from src.methods.database.licenses_manager import LicensesDatabase
from src.methods.database.products_manager import ProductsDatabase
from src.methods.database.carts_manager import ShoppingCartService
shoppingshopping_cart_service = ShoppingCartService()
from loguru import logger
from src.misc import SERVICE_FEE
import asyncio
from collections import defaultdict

class ProcessService:
    @classmethod
    async def validate_order(self,user_id) -> dict:
        """
        Проверяет, валиден ли заказ.
        Возвращает словарь с результатом проверки.
        """
        
        enriched_cart = []
        cart_total = {"cart_id":int,"user_id":int,"subtotal_amount":float,"service_fee":float, "total_amount":float,"payment_method":str}
        result = {"valid": True,"errors": [],"enriched_cart":enriched_cart,"cart_total":cart_total}
        cart_items= await shoppingshopping_cart_service.get_cart_items(user_id) 
        
        if not cart_items:
            result["valid"] = False
            result["errors"].append("Cart is Empty")
            return result    
        # Асинхронно получаем продукты и лицензии
        product_tasks = [ ProductsDatabase.get_product(product_id=item.product_id) for item in cart_items ] 
        license_tasks = [ LicensesDatabase.get_license(license_id=item.license_id) for item in cart_items ]
        # Ждем завершения всех запросов 
        products_results = await asyncio.gather(*product_tasks) 
        licenses_results = await asyncio.gather(*license_tasks) 
        subtotal_amount = 0
        total_amount = 0 
        service_fee = 0
        for item, product, license in zip(cart_items, products_results, licenses_results): 
            if product ==-1:
                result["valid"] = False
                result["errors"].append("Sorry 1 item from your cart has been deleted by seller")
                return result  
            
            elif product[9] == 1: 
                result["errors"].append("Sorry, the beat from your cart was sold exclusively")
                result["valid"] = False
                return result 
            elif not license: 
                result["errors"].append(f"Sorry, the license for '{product[2]}' has been changed.")
                result["valid"] = False
                return result
            elif license[13] == 1: #Если эксклюзив, резервируем
                result = await shoppingshopping_cart_service.reserve_item(user_id=user_id,product_id=product[0])
                if not result: #Уже зарезервировано другим юзером 
                    result["errors"].append(f"Sorry, the beat {product[2]} already reserved.")
                    result["valid"] = False
                    return result
            #тут будет подсчет промокода
            #subtotal_amount+=license[4]*promocode
            cart_total["cart_id"] = item.cart_id 
            subtotal_amount+= license[4]
            
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
        
        if not enriched_cart:
            result["valid"] = False
            result["errors"].append("Cart is Empty")
            return result
        service_fee = subtotal_amount*SERVICE_FEE
        total_amount = subtotal_amount + service_fee
        payment_method = await UsersDatabase.get_value(user_id=user_id,key='default_payment_method')

        cart_total["payment_method"] = payment_method
        cart_total['subtotal_amount']= subtotal_amount
        cart_total['service_fee'] = service_fee
        cart_total['total_amount']= total_amount
        cart_total['user_id'] = user_id
        result["cart_total"] = cart_total 
        result['enriched_cart'] = enriched_cart
        return result
 

    # Функция для генерации итогового сообщения
    @classmethod
    async def generate_cart_summary(self,cart_items):
        # Группируем товары по продавцам и лицензиям
        grouped_items = defaultdict(lambda: defaultdict(list))

        # Собираем все асинхронные задачи для выполнения параллельно
        tasks = []
        for item in cart_items:
            # Асинхронно получаем продавца и лицензию
            tasks.append(
                asyncio.create_task(self.process_item(item, grouped_items))
            )
        
        # Ждем завершения всех асинхронных задач
        await asyncio.gather(*tasks)

        # Формируем текст сообщения
        message_lines = []
        message_lines.append(f"<b>Cart Summary</b>\n")
        
        subtotal_price = 0

        # for name, licenses in grouped_items.items():
        #     message_lines.append(f" **{name}**")  # Продавец
        #     for license_name, items in licenses.items():
        #         license_total = sum(item['price'] for item in items)
        #         total_price += license_total
        #         message_lines.append(f"  📜 {license_name}: ${license_total:.2f}")
        #         for item in items:
        #             message_lines.append(f"    - {item['name']} ${item['price']:.2f}")
        template_len = 30
        for name, licenses in grouped_items.items():
            seller_total = 0.00
            for license_name, items in licenses.items():
                license_total = sum(item['price'] for item in items)
                subtotal_price += license_total
                seller_total += license_total
            count = template_len - len(f"{name}${seller_total:.2f}") 
            message_lines.append(f"<b>{name}"+" "*count+f"${seller_total:.2f}</b>")
                # for item in items:
                #     message_lines.append(f"    - {item['name']} ${item['price']:.2f}")
        # Добавляем итоговую информацию
        count = template_len - len(f"\nSubtotal${subtotal_price:.2f}")+1
        message_lines.append(f"\n<pre>Subtotal"+' '*count+f"${subtotal_price:.2f}")
        discounts = None
        if discounts:
            count = template_len - len(f"Discount${discounts:.2f}")
            message_lines.append(f"Discounts"+' '+count+f"${discounts:.2f}") 
        service_fee = subtotal_price * SERVICE_FEE
        count = template_len - len(f"Service Fee${service_fee:.2f}")
        message_lines.append(f"Service Fee"+' '*count+f"${service_fee:.2f}")
        total_price = subtotal_price + service_fee
        count = template_len - len(f"Total ({len(items)} items)${total_price:.2f}")
        message_lines.append(f"<b>Total ({len(items)} items)"+' '*count+f"${total_price:.2f}</b></pre>")
        return "\n".join(message_lines)

    # Асинхронная функция для обработки одного товара
    @classmethod
    async def process_item(self, item, grouped_items):
    # Получаем seller_id и канал продавца
        seller_id = await ProductsDatabase.get_value(key='user_id', product_id=item['product_id'])
        channel = await UsersDatabase.get_value(key='channel', user_id=seller_id)
        
        # Определяем имя продавца (канал, имя пользователя или ID продавца)
        if channel not in (None, -1):
            name = f"@{channel}"
        else:
            username = await UsersDatabase.get_value(key='username', user_id=seller_id)
            name = f"@{username}" if username not in (None, -1) else str(seller_id)
        
        # Получаем название лицензии
        license_name = await LicensesDatabase.get_value(key='name', license_id=item['license_id'])
        
        # Добавляем товар в сгруппированный список
        grouped_items[name][license_name].append(item)





    

