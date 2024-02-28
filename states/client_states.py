from aiogram.fsm.state import State, StatesGroup


class ShowStates(StatesGroup):
    showProductState = State()

    showCategoryState = State()
    showCategoryProductsState = State()
