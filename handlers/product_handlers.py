from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME
from keyboards.admin_inline_keyboards import make_categories_kb, make_confirm_kb, make_products_kb
from states.admin_states import CategoryStates, ProductStates
from utils.database import Database


product_router = Router()
db = Database(DB_NAME)


@product_router.message(Command('products'))
async def product_list_handler(message: Message):
    await message.answer(
        text="All products:",
        reply_markup=make_products_kb()
    )

@product_router.message(Command('add_product'))
async def add_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.addProductState)
    await message.answer(text="Please, send name for new product...")


@product_router.message(ProductStates.addProductState)
async def insert_product_handler(message: Message, state=FSMContext):
    if db.add_product(new_product=message.text):
        await message.answer(
            f"New product by name '{message.text}' successfully added!"
        )
    else:
        await message.answer(
            f"Something error, resend product"
            f"Send again or click /cancel for cancel process!"
        )
    
@product_router.message(Command('edit_product'))
async def edit_product_handler(message: Message, state=FSMContext):
    await state.set_state(ProductStates.startEditProductState)
    await message.answer(
        text="Select product which you want change:",
        reply_markup=make_products_kb()
    )


@product_router.callback_query(ProductStates.startEditProductState)
async def select_products_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProductStates.finishEditProductState)
    await state.update_data(prod_name=callback.data)
    await callback.message.edit_text(f"Please, send new name for product \"{callback.data}\":")


@product_router.message(ProductStates.finishEditProductState)
async def update_product_handler(message: Message, state=FSMContext):
    if db.check_product_exists(message.text):
        all_data = await state.get_data()
        if db.rename_product(old_name=all_data.get('prod_name'), new_name=message.text):
            await state.clear()
            await message.answer(
                f"Product name successfully modified!"
            )
    else:
        await message.answer(
            f"Product \"{message.text}\" already exists\n"
            f"Send other name or click /cancel for cancel process!"
        )

@product_router.message(Command('del_product'))
async def del_product_handler(message: Message, state=FSMContext):
    await state.set_state(ProductStates.startDeleteProductState)
    await message.answer(
        text="Select product which you want to delete:",
        reply_markup=make_products_kb()
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