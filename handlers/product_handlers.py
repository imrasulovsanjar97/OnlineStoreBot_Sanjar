from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command

from config import DB_NAME
from keyboards.admin_inline_keyboards import categories_kb_4_products, make_confirm_kb, del_1_product_kb
from keyboards.client_keybords import next_prev_kb, get_next_prev_keyboard
from states.admin_states import ProductStates
from states.client_states import ShowStates
from utils.database import Database

product_router = Router()
db = Database(DB_NAME)


@product_router.message(Command('add_product'))
async def add_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.add_SelectCategoryProdState)
    await message.answer(
        text="Please choose a category which you want to add product:",
        reply_markup=categories_kb_4_products()
    )


@product_router.callback_query(ProductStates.add_SelectCategoryProdState)
async def add_product_category_handler(query: CallbackQuery, state: FSMContext):
    await state.update_data(product_category=query.data)
    await state.set_state(ProductStates.add_TitleProdState)
    await query.message.answer("Please, send title for your product...")
    await query.message.delete()


@product_router.message(ProductStates.add_TitleProdState)
async def add_product_title_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_title=message.text)
        await state.set_state(ProductStates.add_TextProdState)
        await message.answer("Please, send full description text for your product:")
    else:
        await message.answer("PLease, send only text...")


@product_router.message(ProductStates.add_TextProdState)
async def add_product_text_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_text=message.text)
        await state.set_state(ProductStates.add_ImageProdState)
        await message.answer("Please, send photo for your product:")
    else:
        await message.answer("PLease, send only text...")


@product_router.message(ProductStates.add_ImageProdState)
async def add_product_image_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(product_image=message.photo[-1].file_id)
        await state.set_state(ProductStates.add_PriceProdState)
        await message.answer("Please, send your product's price:")
    else:
        await message.answer("PLease, send only photo...")


@product_router.message(ProductStates.add_PriceProdState)
async def add_product_price_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(product_price=int(message.text))
        await state.set_state(ProductStates.add_PhoneProdState)
        await message.answer("Please, send phone number for contact with you:")
    else:
        await message.answer("PLease, send only numbers...")


@product_router.message(ProductStates.add_PhoneProdState)
async def add_product_contact_handler(message: Message, state: FSMContext):
    if message.text or message.contact:
        phone = message.text if message.text else message.contact.phone_number
        all_data = await state.get_data()
        print(all_data)
        # title, text, image, price, phone, cat_id, u_id
        result = db.add_product(
            title=all_data.get('product_title'),
            text=all_data.get('product_text'),
            image=all_data.get('product_image'),
            price=all_data.get('product_price'),
            phone=phone,
            cat_id=all_data.get('product_category'),
            u_id=message.from_user.id
        )
        if result:
            await message.answer("Your product successfully added!")
            product = db.get_my_last_product(message.from_user.id)
            await message.answer_photo(
                photo=product[3],
                caption=f"<b>{product[1]}</b>\n\n<b>{product[2]}</b>\n\nPrice: {product[4]}\n\nContact: {product[-1]}"
            )
        else:
            await message.answer("Something went wrong, please try again!")
        await state.clear()
    else:
        await message.answer("PLease, send contact or phone number...")


@product_router.message(Command('products'))
async def products_handler(message: Message, state: FSMContext):
    products = db.get_all_products()
    print(products)
    if products:
        if len(products) == 1:
            product = products[0]
            await message.answer_photo(
                photo=product[3],
                caption=f"<b>{product[1]}</b>\n\n<b>{product[2]}</b>\n\nPrice: {product[4]}\n\nContact: {product[-1]}"
            )
        else:
            await state.set_state(ShowStates.showProductState)
            await state.update_data(index=0)
            await state.update_data(count=len(products))
            await state.update_data(products=products)
            product = products[0]
            await message.answer_photo(
                photo=product[3],
                caption=f"<b>{product[1]}</b>\n\n<b>{product[2]}</b>\n\nPrice: {product[4]}\n\nContact: {product[-1]}",
                reply_markup=next_prev_kb,
                parse_mode="HTML"
            )
    else:
        await message.answer("No products found.")


@product_router.callback_query(ShowStates.showProductState)
async def show_product_callback_query(query: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    index = all_data["index"]
    count = all_data["count"]
    products = all_data["products"]

    if query.data == "next":
        if index == count - 1:
            index = 0
        else:
            index += 1
    else:
        if index == 0:
            index = count - 1
        else:
            index -= 1

    await state.update_data(index=index)
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=products[index][3],
            caption=f"<b>{products[index][1]}</b>\n\n<b>{products[index][2]}</b>\n\nPrice: {products[index][4]}\n\nContact: {products[index][-1]}",
            parse_mode="HTML"
        ),
        reply_markup=next_prev_kb
    )


@product_router.message(Command('all_products'))
async def all_products_handler(message: Message, state: FSMContext):
    categories = db.get_categories()
    await state.set_state(ShowStates.showCategoryState)
    await message.answer(
        text="Please select a category to view the products.",
        reply_markup=categories_kb_4_products()
    )


@product_router.callback_query(ShowStates.showCategoryState)
async def show_category_callback_query(query: CallbackQuery, state: FSMContext):
    products = db.get_all_products(query.data)
    await state.set_state(ShowStates.showCategoryProductsState)
    await state.update_data(products=products)

    if products:
        count = len(products)
        s = ""
        if count <= 10:
            for i in range(count):
                s += f"<b>{i + 1}.</b> {products[i][1]}\n"
            kb = get_next_prev_keyboard(all_count=count, count=count)
        await query.message.edit_text(
            text=s, reply_markup=kb, parse_mode="HTML"
        )


@product_router.callback_query(ShowStates.showCategoryProductsState)
async def show_category_callback_query(query: CallbackQuery, state: FSMContext):
    index = int(query.data)
    all_data = await state.get_data()
    products = all_data['products']

    await query.message.answer_photo(
        photo=products[index][3],
        caption=f"<b>{products[index][1]}</b>\n\n<b>{products[index][2]}</b>\n\nPrice: {products[index][4]}\n\nContact: {products[index][-1]}",
        parse_mode="HTML"
    )

@product_router.message(Command('del_product'))
async def del_product_handler(message: Message, state=FSMContext):
    await state.set_state(ProductStates.startDeleteProductState)
    await message.answer(
        text="Select product which you want to delete:",
        reply_markup=del_1_product_kb()
    )


@product_router.callback_query(ProductStates.startDeleteProductState)
async def select_product_del_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProductStates.finishDeleteProductState)
    await state.update_data(prod_name=callback.data)
    await callback.message.edit_text(
        text=f"Do you want to delete product \"{callback.data}\":",
        reply_markup=make_confirm_kb()
    )


@product_router.callback_query(ProductStates.finishDeleteProductState)
async def remove_category_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'YES':
        all_data = await state.get_data()
        if db.delete_product(all_data.get('prod_name')):
            await callback.message.answer("Product successfully deleted!")
            await callback.message.delete()
            await state.clear()
        else:
            await callback.message.answer(
                f"Something went wrong!"
                f"Try again later or click /cancel for cancel process!"
            )
    else:
        await state.clear()
        await callback.message.answer('Process canceled!')
        await callback.message.delete()

@product_router.message(F.text)
async def search_by_name_handler(message: Message):
    def cyrillic_to_latin(word):
        cyrillic_to_latin_map = {
            'а': 'a', 'б': 'b', 'ц': 'c', 'д': 'd', 'е': 'e', 'ф': 'f', 'г': 'g',
            'х': 'h', 'и': 'i', 'ж': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'в': 'v',
            'ь': "'", 'ъ': "'", 'ы': 'y', 'з': 'z',
            'А': 'A', 'Б': 'B', 'Ц': 'C', 'Д': 'D', 'Е': 'E', 'Ф': 'F', 'Г': 'G',
            'Х': 'H', 'И': 'I', 'Ж': 'J', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
            'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'В': 'V',
            'Ь': "'", 'Ъ': "'", 'Ы': 'Y', 'З': 'Z'
        }

        latin_word = ''
        for char in word:
            if char in cyrillic_to_latin_map:
                latin_word += cyrillic_to_latin_map[char]
            else:
                latin_word += char

        return latin_word
    
    title = db.get_all_products()
    for i in range(len(title)):
        if cyrillic_to_latin(message.text) in title[i][1]:
            await message.answer_photo(
                photo=title[i][3],
                caption=f"<b>{title[i][1]}</b>\n\n<b>{title[i][2]}</b>\n\nPrice: {title[i][4]}\n\nContact: {title[i][-1]}",
                parse_mode="HTML"
            )    