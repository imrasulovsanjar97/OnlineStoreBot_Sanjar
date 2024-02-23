from aiogram.fsm.state import State, StatesGroup


class CategoryStates(StatesGroup):
    addCategoryState = State()

    startEditCategoryState = State()
    finishEditCategoryState = State()

    startDeleteCategoryState = State()
    finishDeleteCategoryState = State()

    
class ProductStates(StatesGroup):
    addProductState = State()
    
    startEditProductState = State()
    finishEditProductState = State()

    startDeleteProductState = State()
    finishDeleteProductState = State()