import logging
from models import Base, User, Employer, Vacancy, Recruiter, Resume
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
API_TOKEN = "1707050052:AAFB1TJDLuSzYTRne-cTeEEp-Lph_vyEwVA"

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


profile_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons1 = ["РАБОТОДАТЕЛЬ", "РЕКРУТЕР"]
profile_board.add(*buttons1)
create_vacancy_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
create_vacancy_board.add("ЗАПОЛНИТЬ ЗАЯВКУ")
pay_level_list = ['LIGHT', 'MEDIUM', 'HARD', 'PRO']
pay_level_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
pay_level_keyboard.add(*pay_level_list)
pay_level_dict = {
    'LIGHT': [[1, 500], 1],
    'MEDIUM': [[501, 5000], 2],
    'HARD': [[5001, 10000], 3],
    'PRO': [[10001, 10000000], 3]
}
keyboard_activate = types.ReplyKeyboardMarkup(resize_keyboard=True)
activate_buttons = ["Запустить подбор", "Сохранить в черновик", "Отменить"]
keyboard_activate.add(*activate_buttons)
level_recruiter_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
level_recruiter_board.add("УРОВНЬ LIGHT", "ОТПРАВИТЬ РЕЗЮМЕ")
admin_buttons = types.InlineKeyboardMarkup()


class AdminState(StatesGroup):
    loign = State()


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


class RecruiterRegistry(StatesGroup):
    register = State()
    fio = State()
    years = State()
    specialization = State()
    tools = State()
    difficulties = State()
    invitation = State()
    letter = State()
    refusal = State()


@dp.message_handler(commands=['admin'])
async def become_admin(message: types.Message):
    await AdminState.loign.set()
    await message.answer("Введите ключ, чтобы получить возможность рассмотрения заявки")

@dp.message_handler(state=AdminState.loign)
async def login(message: types.Message, state: FSMContext):
    if message.text == "d873ec68-2729-4c5d-9753-39540c011c75":
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        user.superuser = True
        session.commit()
        session.close()
        await message.answer("""Вы получили права модератора. 
Вам будут поступать резюме рекрутеров для рассмотрения уровня""")
    else:
        await message.answer("Неверный пароль")
    await state.finish()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if not session.query(User).filter_by(telegram_id=message.from_user.id).all():
        session.add(User(telegram_id=message.from_user.id))
        session.commit()
        session.close()
    await message.answer("Чтобы посмотреть доступные команды введите /help. Выберите категорию:",
                         reply_markup=profile_board
                         )

# ОБРАБОТКА ЗАПОЛНЕНИЯ ЗАЯВКИ


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
    await message.answer(text, reply_markup=create_vacancy_board)


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
        vacancy.numb_level = pay_level_dict[message.text][1]
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
    if pay_level_dict[pay_level][0][0] <= salary <= pay_level_dict[pay_level][0][1]:
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
    vacancy = session.query(Vacancy).filter_by(employer=employer, finite_state=9).first()
    if message.text == "Запустить подбор":
        vacancy.active = True
        vacancy.finite_state = 10
        session.commit()
        session.close()
        await state.finish()
        await message.answer("Заявка добавлена в выдачу, вам придёт сообщение, как только на неё откликнутся!")
    elif message.text == "Сохранить в черновик":
        vacancy.finite_state = 10
        session.commit()
        session.close()
        await state.finish()
        await message.answer("Заявка сохранена в черновик. Выберите команду /drafts чтобы отобразить ваши черновики")
    elif message.text == "Отменить":
        session.delete(vacancy)
        session.commit()
        session.close()
        await state.finish()
        await message.answer("Заявка удалена")
    else:
        await message.answer("Выберите один из предложенных вариантов", reply_markup=keyboard_activate)


@dp.message_handler(Text(equals="РЕКРУТЕР"))
async def recruiter_start(message: types.Message):
    if not session.query(Recruiter).filter_by(user_id=message.from_user.id).first():
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        session.add(Recruiter(user=user))
        session.commit()
        session.close()
        text_hello = """Здравствуйте, {0} {1}. 
    Рад приветствовать тебя!
    Заработай больше на поиске персонала. Закрывай заявки в любое время. Делай то, что тебе нравится!""".format(
                message.from_user.first_name,
                message.from_user.last_name,
            )
        await message.answer(text_hello)
        text_levels = """
    Для рекрутеров доступны 4 уровня профиля: LIGHT, MEDIUM, HARD, PRO. 
    LIGHT - доступны заявки с вознаграждением рекрутеру до 500 рублей. 
    MEDIUM – заявки стоимостью до 5000 руб. Переход при закрытии 3-х  заявок от разных работодателей на уровне LIGHT.
    HARD – заявки стоимостью от 5000 до 10000 руб. Переход при закрытии 7-ми заявок разных работодателей на уровне MEDIUM.
    PRO – заявки стоимостью от 10000 руб. Переход при закрытии 10-ти заявок любых работодателей на уровне HARD.
    """
        await message.answer(text_levels)
        text_question = """
    Вы можете продолжить на уровне LIGHT или отправить резюме, я рассмотрю его и присвою соответствующий уровень.
    """
        await RecruiterRegistry.register.set()
        await message.answer(text_question, reply_markup=level_recruiter_board)
    else:
        await message.answer("У вас уже есть профиль рекрутера, выберите команду /placeholder чтобы получить заявки")


@dp.message_handler(state=RecruiterRegistry.register)
async def choose_level(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    if message.text == "УРОВЕНЬ LIGHT":
        recruiter.level = "LIGHT"
        recruiter.level_numb = 1
        session.commit()
        session.close()
        await state.finish()
        await message.answer("Вам назначен уровень LIGHT")
    elif message.text == "ОТПРАВИТЬ РЕЗЮМЕ":
        session.add(Resume(recruiter=recruiter))
        session.commit()
        session.close()
        await message.answer("""
Я всегда рад опытным рекрутерам! Отлично, что вы решили работать со мной!
Расскажите мне о себе и в течение 3- х дней я приму решение:
""")
        await message.answer("Заполните форму, чтобы перейти на следующий уровень.")
        await message.answer("Ваше ФИО:")
        await RecruiterRegistry.next()
    else:
        await message.answer("Выберите один из предложенных вариантов!")


@dp.message_handler(state=RecruiterRegistry.fio)
async def set_fio(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.fio = message.text
    session.commit()
    session.close()
    await message.answer("Сколько лет вы в подборе:")
    await RecruiterRegistry.next()


@dp.message_handler(state=RecruiterRegistry.years)
async def set_years(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.years = message.text
    session.commit()
    session.close()
    await message.answer("В какой области вы специализируетесь:")
    await RecruiterRegistry.next()


@dp.message_handler(state=RecruiterRegistry.specialization)
async def set_specialization(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.specialization = message.text
    session.commit()
    session.close()
    await message.answer("Какими инструментами пользуетесь при подборе:")
    await RecruiterRegistry.next()


@dp.message_handler(state=RecruiterRegistry.tools)
async def set_tools(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.tools = message.text
    session.commit()
    session.close()
    await message.answer("С какими трудностями сталкивались при подборе")
    await RecruiterRegistry.next()


@dp.message_handler(state=RecruiterRegistry.difficulties)
async def set_difficulties(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.difficulties = message.text
    session.commit()
    session.close()
    await message.answer("Напишите краткое приглашение соискателю на вакансию")
    await RecruiterRegistry.next()


@dp.message_handler(state=RecruiterRegistry.invitation)
async def set_invitation(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.invitation = message.text
    session.commit()
    session.close()
    await message.answer("""Вы не можете долго закрыть заявку и понимаете, что заработная плата не в рынке. 
Напишите письмо работодателю с предложением откорректировать заявку.""")
    await RecruiterRegistry.next()


@dp.message_handler(state=RecruiterRegistry.letter)
async def set_letter(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.letter = message.text
    session.commit()
    session.close()
    await message.answer("Не все соискатели подошли. Как вы откажете соискателю?")
    await RecruiterRegistry.next()


@dp.message_handler(state=RecruiterRegistry.refusal)
async def set_refusal(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    resume.refusal = message.text
    session.commit()
    await message.answer("Ваше резюме:")
    await message.answer(resume)
    await message.answer("Я рассмотрю ваше резюме в течение 3 дней и вам будет присвоен соответствующий уровень")
    await state.finish()
    admins = session.query(User).filter_by(superuser=True).all()
    for admin in admins:
        await bot.send_message(admin.telegram_id, "Резюме от рекрутера для рассмотрения")
        await bot.send_message(admin.telegram_id, resume)
        admin_buttons.add(
            types.InlineKeyboardButton("LIGHT", callback_data="LIGHT " + "1 " + str(message.from_user.id)),
            types.InlineKeyboardButton("MEDIUM", callback_data="MEDIUM " + "1 " + str(message.from_user.id)),
            types.InlineKeyboardButton("HARD", callback_data="HARD " + "1 " + str(message.from_user.id)),
            types.InlineKeyboardButton("LIGHT", callback_data="LIGHT " + "1 " + str(message.from_user.id)),
        )
    session.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


