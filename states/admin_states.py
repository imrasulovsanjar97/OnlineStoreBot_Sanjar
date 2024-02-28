from aiogram.fsm.state import State, StatesGroup


class CategoryStates(StatesGroup):
    addCategoryState = State()

    startEditCategoryState = State()
    finishEditCategoryState = State()

    startDeleteCategoryState = State()
    finishDeleteCategoryState = State()


class ProductStates(StatesGroup):
    add_SelectCategoryProdState = State()
    add_TitleProdState = State()
    add_TextProdState = State()
    add_ImageProdState = State()
    add_PriceProdState = State()
    add_PhoneProdState = State()

    startDeleteProductState = State()
    finishDeleteProductState = State()