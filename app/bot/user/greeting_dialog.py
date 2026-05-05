from aiogram.fsm.state import State, StatesGroup


class GreetingSG(StatesGroup):
    welcome = State()
    returning = State()
