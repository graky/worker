import logging
from models import Base, User, Employer, Vacancy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
API_TOKEN = "1707050052:AAG2mDycSulRLtoqUm4AX8FLYlu0gH5aDVk"

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
user = "postgre"
password = "postgre"
db_name = "bot"
db_host = "localhost"
engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (str(user), str(password), str(db_host), str(db_name)))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
DBSession.bind = engine
session = DBSession()


keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons1 = ["РАБОТОДАТЕЛЬ", "РЕКРУТЕР"]
keyboard1.add(*buttons1)
keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard2.add("ЗАПОЛНИТЬ ЗАЯВКУ")
pay_level_list = ['LIGHT', 'MEDIUM', 'HARD', 'PRO']
pay_level_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
pay_level_keyboard.add(*pay_level_list)
pay_level_dict = {'LIGHT': [1, 500], 'MEDIUM': [501, 5000], 'HARD': [5001, 10000], 'PRO': [10001, 10000000]}
keyboard_activate = types.ReplyKeyboardMarkup(resize_keyboard=True)
activate_buttons = ["Запустить подбор", "Сохранить в черновик", "Отменить"]
keyboard_activate.add(*activate_buttons)
class EmployerState(StatesGroup):
    company = State()
    website = State()
    name = State()
    duties = State()
    requirements = State()
    conditions = State()
    level = State()
    salary = State()
    activate = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if not session.query(User).filter_by(telegram_id=message.from_user.id).all():
        session.add(User(telegram_id=message.from_user.id))
        session.commit()
        session.close()
    await message.answer("Чтобы посмотреть доступные команды введите /help. Выберите категорию:",
                         reply_markup=keyboard1
                         )


@dp.message_handler(Text(equals="РАБОТОДАТЕЛЬ"))
async def employer_start(message: types.Message):
    if not session.query(Employer).filter_by(user_id=message.from_user.id).first():
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        session.add(Employer(user=user))
        session.commit()
        session.close()
    text = """Здравствуйте, {0} {1}. 
Не тратьте время на поиск сотрудников. Делегируйте это мне! 
Со мной работает {2} рекрутеров со всей страны!
Внимательно заполните форму заявки, выберите уровень вознаграждения за подбор и мотивируйте рекрутеров заняться именно вашей заявкой.""".format(
            message.from_user.first_name,
            message.from_user.last_name,
            len(session.query(Employer).all())
        )
    await message.answer(text, reply_markup=keyboard2)


@dp.message_handler(Text(equals="ЗАПОЛНИТЬ ЗАЯВКУ"))
async def vacancy_start(message: types.Message):
    if employer := session.query(Employer).filter_by(user_id=message.from_user.id).first():
        session.add(Vacancy(employer=employer, finite_state=1))
        session.commit()
        session.close()
        text = "Введите наименование компании"
        await message.answer(text)
        await EmployerState.company.set()


@dp.message_handler(state=EmployerState.company)
async def set_company(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=1).first()
    vacancy.company = message.text
    vacancy.finite_state = 2
    session.commit()
    session.close()
    await EmployerState.next()
    await message.answer("Введите сайт компании")


@dp.message_handler(state=EmployerState.website)
async def set_website(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=2).first()
    vacancy.website = message.text
    vacancy.finite_state = 3
    session.commit()
    session.close()
    await EmployerState.next()
    await message.answer("Введите наименование вакантной должности")


@dp.message_handler(state=EmployerState.name)
async def set_name(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=3).first()
    vacancy.name = message.text
    vacancy.finite_state = 4
    session.commit()
    session.close()
    await EmployerState.next()
    await message.answer("Введите обязанности будущего сотрудника")


@dp.message_handler(state=EmployerState.duties)
async def set_duties(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=4).first()
    vacancy.duties = message.text
    vacancy.finite_state = 5
    session.commit()
    session.close()
    await EmployerState.next()
    await message.answer("""Введите требования для будущего сотрудника
- опыт работы:

- образование:

- навыки и умения:

- иное:""")


@dp.message_handler(state=EmployerState.requirements)
async def set_requirements(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=5).first()
    vacancy.requirements = message.text
    vacancy.finite_state = 6
    session.commit()
    session.close()
    await EmployerState.next()
    await message.answer("""Какие условия работы вы готовы предложить будущему сотруднику
- график работы:

- заработная плата:

- характер работы:

- иное:""")


@dp.message_handler(state=EmployerState.conditions)
async def set_conditions(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=6).first()
    vacancy.conditions = message.text
    vacancy.finite_state = 7
    session.commit()
    session.close()
    await EmployerState.next()
    await message.answer("""Выберите уровень вознаграждения рекрутеру за подбор. От суммы вознаграждения зависит, какого уровня рекрутеры увидят вашу заявку.

LIGHT (заявки до 500 рублей)

MEDIUM (от 501 до 5000 руб.)

HARD (от 5001 до 10000 руб.)

PRO ( выше 10000 руб.)""", reply_markup=pay_level_keyboard)


@dp.message_handler(state=EmployerState.level)
async def set_level(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=7).first()
    if message.text in pay_level_list:
        vacancy.pay_level = message.text
        vacancy.finite_state = 8
        session.commit()
        session.close()
        await EmployerState.next()
        await message.answer("""Введите сумму вознаграждения рекрутеру""")
    else:
        await message.answer("Выберите один из предложенных вариантов!")


@dp.message_handler(state=EmployerState.salary)
async def set_salary(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=8).first()
    try:
        salary = int(message.text)
    except ValueError:
        await message.answer("Введите валидные данные. Одно число без дополнительных знаков")
        return
    pay_level = vacancy.pay_level
    if pay_level_dict[pay_level][0] <= salary <= pay_level_dict[pay_level][1]:
        vacancy.salary = salary
        vacancy.finite_state = 9
        session.commit()
        await EmployerState.next()
        await message.answer("""Вами выбран уровень {0}! 
После модерации я покажу ее {1} рекрутерам и они предложат целевых кандидатов, если заявка их заинтересует.
Вам останется только сделать свой выбор. А пока вы можете заняться более важными делами. До связи, {2} {3}!""".format(
            pay_level,
            150,
            message.from_user.first_name,
            message.from_user.last_name,
        ))
        await message.answer(vacancy, reply_markup=keyboard_activate)
        session.close()
    else:
        await message.answer("Введенное значение не удовлетворяет выбранному уровню.")


@dp.message_handler(state=EmployerState.activate)
async def set_activate(message: types.Message, state: FSMContext):
    employer = session.query(Employer).filter_by(user_id=message.from_user.id).first()
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=8).first()
    if message.text == "Запустить подбор":
        vacancy.active = True
        vacancy.finite_state = 9
        session.commit()
        session.close()
        await message.answer("Заявка добавлена в выдачу, вам придёт сообщение, как только на неё откликнутся!")
    elif message.text == "Сохранить в черновик":
        vacancy.finite_state = 9
        session.commit()
        session.close()
        await message.answer("Заявка сохранена в черновик. Выберите команду /drafts чтобы отобразить ваши черновики")
    elif message.text == "Отменить":
        vacancy.delete()
        session.commit()
        session.close()
        await message.answer("Заявка удалена")
    else:
        await message.answer("Выберите один из предложенных вариантов", reply_markup=keyboard_activate)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


