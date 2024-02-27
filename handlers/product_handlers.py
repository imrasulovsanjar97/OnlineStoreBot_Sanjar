from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME
from keyboards.admin_inline_keyboards import select_categories_kb, make_confirm_kb, make_1_product_kb, get_1_product_kb
from states.admin_states import CategoryStates, ProductStates
from utils.database import Database


product_router = Router()
db = Database(DB_NAME)


@product_router.message(Command('products'))
async def product_list_handler(message: Message):
    products = db.get_all_products(message.from_user.id)
    for product in products[:len(products)]:
        await message.answer_photo(
            photo = product[3],
            caption=f"{product[1]}\n\n{product[2]}\n\nPrice:{product[4]}\n\nContact: {product[-1]}"
        )
        

@product_router.message(Command('add_product'))
async def add_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.addSelectCategoryProdState)
    await message.answer(
        text="Please, select category for product:",
        reply_markup=select_categories_kb()                 
        )


@product_router.callback_query(ProductStates.addSelectCategoryProdState)
async def insert_product_handler(query: CallbackQuery, state=FSMContext):
    await state.update_data(product_category=query.data)
    await state.set_state(ProductStates.addProductTitleState)
    await query.message.answer('Please enter the title of the product: ')
    await query.message.delete()

@product_router.message(ProductStates.addProductTitleState)
async def insert_product_title(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_title=message.text)
        await state.set_state(ProductStates.addProductTextState)
        await message.answer(
            f"Please enter the description of the product:"
        )
    else:
        await message.answer(
            f"Please send only text!"
        )
    
@product_router.message(ProductStates.addProductTextState)
async def insert_product_text(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_text=message.text)
        await state.set_state(ProductStates.addProductImageState)
        await message.answer(
            f"Please send image of the product:"
        )
    else:
        await message.answer(
            f"Please send only text!"
        )

@product_router.message(ProductStates.addProductImageState)
async def insert_product_image(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(product_image=message.photo[-1].file_id)
        await state.set_state(ProductStates.addProductPriceState)
        await message.answer(
                f"Please write price of the product:"
            )
    else: await message.answer(
        f'Please send only photo!'
    )
        
@product_router.message(ProductStates.addProductPriceState)
async def insert_product_price(message: Message, state: FSMContext):
    if message.text.isdigit:
        await state.update_data(product_price=int(message.text))
        await state.set_state(ProductStates.addProductPhoneState)
        await message.answer(
            f"Please send phone for the contact:"
            )
    else: await message.answer(
        f'Please send only numbers!'
    )

@product_router.message(ProductStates.addProductPhoneState)
async def insert_product_phone(message: Message, state: FSMContext):
    if message.text or message.contact:
        phone = message.text if message.text else message.contact.phone_number
        all_data = await state.get_data()
        result = db.add_product(
            title=all_data.get('product_title'),
            text=all_data.get('product_text'),
            image=all_data.get('product_image'),
            price=all_data.get("product_price"),
            phone=phone,
            cat_id=all_data.get('product_category'),
            u_id=message.from_user.id
        )
        if result:
            await message.answer("Your product successfully addded!")
            product =   db.get_my_last_product(message.from_user.id)
            await message.answer_photo(
                photo = product[3],
                caption=f"{product[1]}\n\n{product[2]}\n\nPrice:{product[4]}\n\nContact: {product[-1]}"
            )
        else:
            await message.answer("Something went wrong, please try later!")
        await state.clear()
    else: await message.answer(
        f'Please send contact or phone number!'
    )


@product_router.message(Command('edit_product'))
async def edit_product_handler(message: Message, state=FSMContext):
    await state.set_state(ProductStates.startEditProductState)
    await message.answer(
        text="Select product which you want change:",
        reply_markup=make_1_product_kb()
    )

@product_router.callback_query(ProductStates.startEditProductState)
async def product_handler(query: CallbackQuery, state:FSMContext):
    if db.rename_product(query.message.text):
        await state.set_state(ProductStates.finishEditProductState)
        await query.message.answer(
            text="All date:",
            reply_markup=get_1_product_kb()
    )
         
   
    #for product in products[:len(products)]:  
    #   await query.message.answer(
     #       text="Select data which you want change:",
     #       reply_markup=get_1_product_kb()
    #)

#@product_router.callback_query(ProductStates.startEditProductState)
#async def select_products_handler(callback: CallbackQuery, state: FSMContext):
#    await state.set_state(ProductStates.finishEditProductState)
 #   await state.update_data(prod_name=callback.data)
 #   await callback.message.edit_text(f"Please, send new name for product \"{callback.data}\":")


@product_router.message(ProductStates.finishEditProductState)
async def update_product_handler(message: Message, state=FSMContext):
    all_data = await state.get_data()
    if db.rename_product(old_name=all_data.get('prod_name'), new_name=message.text):
        await state.clear()
        await message.answer(
            f"Product title successfully modified!"
        )
   
@product_router.message(Command('del_product'))
async def del_product_handler(message: Message, state=FSMContext):
    await state.set_state(ProductStates.startDeleteProductState)
    await message.answer(
        text="Select product which you want to delete:",
        reply_markup=get_1_product_kb()
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

@product_router.message(Command('products'))
async def product_list_handler(message: Message):
    await message.answer(
        text="All products:",
        reply_markup=make_1_product_kb()
    )