from aiogram.fsm.state import State, StatesGroup


class CategoryStates(StatesGroup):
    addCategoryState = State()

    startEditCategoryState = State()
    finishEditCategoryState = State()

    startDeleteCategoryState = State()
    finishDeleteCategoryState = State()

    
class ProductStates(StatesGroup):
    addSelectCategoryProdState = State()
    addProductTitleState = State()
    addProductTextState = State()
    addProductImageState = State()
    addProductPriceState = State()
    addProductPhoneState = State()

    
    startEditProductState = State()
    selectEditProductsState = State()
    selectDataProductsState = State()
    finishEditProductState = State()

    startDeleteProductState = State()
    finishDeleteProductState = State()