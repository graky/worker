import logging
from models import Base, User, Employer, Vacancy, Recruiter, Resume, Question, Answer, InWork
from models import get_or_create
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = ""
ADMIN_KEY = "d873ec68-2729-4c5d-9753-39540c011c75"
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
    'PRO': [[10001, 10000000], 4]
}
keyboard_activate = types.ReplyKeyboardMarkup(resize_keyboard=True)
activate_buttons = ["Запустить подбор", "Сохранить в черновик", "Отменить"]
keyboard_activate.add(*activate_buttons)
level_recruiter_board = types.ReplyKeyboardMarkup(resize_keyboard=True)
level_recruiter_board.add("УРОВЕНЬ LIGHT", "ОТПРАВИТЬ РЕЗЮМЕ")
next_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
next_button.add("ДАЛЕЕ")
star_test_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
star_test_button.add("НАЧАТЬ ТЕСТ")
finish_test_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
finish_test_button.add("ЗАВЕРШИТЬ ТЕСТ")
question1 = ["Я буду искать кандидатов",
             [
                 "Telegram",
                 "Соц сети, работные сайты",
                 "На рынке",
                 "Сайты знакомств",
                 "Дам объявление",
                 "Переманю"
             ],
             False]

question2 = ["Прежде, чем отправить кандидата на рассмотрение работодателю, я",
             [
                "Проведу телефонное интервью",
                "Созвонюсь по видео связи",
                "Встречусь вживую при необходимости",
                "Только пообщаюсь по переписке",

             ],
             False,
             ]

question3 = ["Для того, чтобы начать зарабатывать на закрытии заявок мне нужно",
             [
                "Быть ИП",
                "Иметь юр лицо",
                "Открыть самозанятость",
                "Быть фрилансером",

             ],
             False,
             ]


async def admin_set_level(admin_id, lvl, numb_lvl, recruiter_id):
    recruiter = session.query(Recruiter).filter_by(user_id=recruiter_id).first()
    resume = session.query(Resume).filter_by(recruiter_id=recruiter.id).first()
    if not resume.reviewed:
        resume.reviewed = True
        recruiter.level = lvl
        recruiter.level_numb = numb_lvl
        session.commit()
        session.close()
        await bot.send_message(recruiter_id, f"Поздравляем, вам назначен уровень {lvl}!")
        await bot.send_message(admin_id, "Уровень рекрутеру назначен!")
    else:
        await bot.send_message(admin_id, "Резюме рекрутера уже было рассмотрено")


async def set_light_level(user_id):
    await bot.send_message(user_id, "Ваш уровень LIGHT. Давайте пройдём небольшое обучение.", reply_markup=next_button)


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
    text1 = State()
    text2 = State()
    text3 = State()
    text4 = State()
    text5 = State()
    test1 = State()
    test2 = State()
    test3 = State()
    finish_test = State()


@dp.message_handler(commands=['admin'])
async def become_admin(message: types.Message):
    await AdminState.loign.set()
    await message.answer("Введите ключ, чтобы получить возможность рассмотрения заявки")


@dp.message_handler(commands=['get_vacancies'])
async def get_vacancies(message: types.Message):
    if recruiter := session.query(Recruiter).filter_by(user_id=message.from_user.id).first():
        if recruiter.finished_educ:
            vacancies = session.query(Vacancy).filter(
                Vacancy.numb_level <= recruiter.level_numb,
                Vacancy.active == True
            ).all()
            for vacancy in vacancies:
                recruiter_buttons = types.InlineKeyboardMarkup()
                recruiter_buttons.add(
                    types.InlineKeyboardButton("ВЗЯТЬ В РАБОТУ",
                                               callback_data="in_work " + f"{vacancy.id} " + f"{recruiter.id}"),
                    types.InlineKeyboardButton("ПРЕДЛОЖИТЬ КАНДИДАТА",
                                               callback_data="add_cand " + f"{vacancy.id} " + f"{recruiter.id}"),
                )
                await message.answer(vacancy, reply_markup=recruiter_buttons)
        else:
            await message.answer("""Вы ещё не прошли обучение. 
Чтобы пройти обучение, воспользуйтесь командой /start далее выберите РЕКРУТЕР и следуйте инструкциям.""")
    else:
        await message.answer("""У вас ещё  нет профиля рекрутера. 
Чтобы создать профиль рекрутера, воспользуйтесь командой /start далее выберите РЕКРУТЕР и следуйте инструкциям.""")


@dp.message_handler(commands=['in_work'])
async def in_work(message: types.Message):
    if recruiter := session.query(Recruiter).filter_by(user_id=message.from_user.id).first():
        if recruiter.finished_educ:
            vacancies_in_work = session.query(InWork).filter(
                InWork.recruiter_id == recruiter.id
            ).all()
            for vacancy_in_work in vacancies_in_work:
                vacancy = session.query(Vacancy).get(vacancy_in_work.vacancy_id)
                recruiter_buttons = types.InlineKeyboardMarkup()
                recruiter_buttons.add(
                    types.InlineKeyboardButton("ПРЕДЛОЖИТЬ КАНДИДАТА",
                                               callback_data="add_cand " + f"{vacancy.id} " + f"{recruiter.id}"),
                )
                await message.answer(vacancy, reply_markup=recruiter_buttons)
        else:
            await message.answer("""Вы ещё не прошли обучение. 
Чтобы пройти обучение, воспользуйтесь командой /start далее выберите РЕКРУТЕР и следуйте инструкциям.""")
    else:
        await message.answer("""У вас ещё  нет профиля рекрутера. 
Чтобы создать профиль рекрутера, воспользуйтесь командой /start далее выберите РЕКРУТЕР и следуйте инструкциям.""")


@dp.message_handler(state=AdminState.loign)
async def login(message: types.Message, state: FSMContext):
    if message.text == ADMIN_KEY:
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
        if not session.query(Recruiter).filter_by(user_id=message.from_user.id).first().finished_educ:
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
            await message.answer(
                "У вас уже есть профиль рекрутера, выберите команду /placeholder чтобы получить заявки")


@dp.message_handler(state=RecruiterRegistry.register)
async def choose_level(message: types.Message, state: FSMContext):
    recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
    if message.text == "УРОВЕНЬ LIGHT":
        recruiter.level = "LIGHT"
        recruiter.level_numb = 1
        session.commit()
        session.close()
        await RecruiterRegistry.text1.set()
        await set_light_level(message.from_user.id)
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
    await message.answer("""Я рассмотрю ваше резюме в течение 3 дней и вам будет присвоен соответствующий уровень. 
На время рассмотрения вам будет присвоен уровень LIGHT.""")
    await set_light_level(message.from_user.id)
    await RecruiterRegistry.next()
    admins = session.query(User).filter_by(superuser=True).all()
    admin_buttons = types.InlineKeyboardMarkup()
    admin_buttons.add(
        types.InlineKeyboardButton("LIGHT", callback_data="set_lvl " + "LIGHT " + "1 " + str(message.from_user.id)),
        types.InlineKeyboardButton("MEDIUM", callback_data="set_lvl " + "MEDIUM " + "2 " + str(message.from_user.id)),
        types.InlineKeyboardButton("HARD", callback_data="set_lvl " + "HARD " + "3 " + str(message.from_user.id)),
        types.InlineKeyboardButton("PRO", callback_data="set_lvl " + "PRO " + "4 " + str(message.from_user.id)),
    )
    for admin in admins:
        await bot.send_message(admin.telegram_id, "Резюме от рекрутера для рассмотрения")
        await bot.send_message(admin.telegram_id, resume)
        await bot.send_message(admin.telegram_id, "Назначьте уровень рекрутеру", reply_markup=admin_buttons)
    session.close()


@dp.message_handler(state=RecruiterRegistry.text1)
async def first_text(message: types.Message, state: FSMContext):
    if message.text == "ДАЛЕЕ":
        await message.answer("""Мир поделен на две части: тот, кто предлагает работу, и тот, кто эту работу выполняет.
 
Рекрутер относится ко второй категории.

Мы с вами выполняем работу по поиску людей, которые согласны выполнять работу тех, кто ее предоставляет.

Требуется понимать - насколько качественно мы выполним нашу с вами работу и как быстро предоставим нужного человека – от этого зависит наше будущее, как профессионала.
""", reply_markup=next_button)

        await RecruiterRegistry.next()
    else:
        await message.answer("Нажмите ДАЛЕЕ, чтобы продолжить обучение.")


@dp.message_handler(state=RecruiterRegistry.text2)
async def second_text(message: types.Message, state: FSMContext):
    if message.text == "ДАЛЕЕ":
        await message.answer("""Сейчас искать людей гораздо проще, когда мир технологий развит и продолжает развиваться. Использовать можно все возможные ресурсы:
        
- во-первых, telegram. Есть множество сообществ, где общаются специалисты той или иной области. 
Подписываемся на их группы и каналы и общаемся с ними от лица представителя работодателя. Кто-то да откликнется.

- социальные сети. Технология та же – используем тематические группы и форумы и находим тех, кого заинтересуют наши предложения.

- специализированные площадки, сайты по поиску работы. Сейчас их множество, но многие могут быть платными. 
Их можно использовать, но нужно быть готовыми платить за услуги по предоставлению резюме.

- сайты знакомств. Даже такие сайты имеются в инструментах профессионального рекрутера. 
Можно завязывать диалог, а затем плавно переходить к предложению по работе. Если попадете в бан, то ничего страшного. 
Поверьте, многие, обдумав потом предложение, соглашаются на оффер.

- ну и конечно печатные СМИ и объявления на местных досках. 
Сколько бы людей не пользовалось интернетом, иногда выгоднее наклеить объявление на остановке и получить требуемый отклик.

- прямой поиск. Когда мы точно знаем, где находится требуемый специалист, и пытаемся его переманить. 
Обычно это уже уровень PRO, но и новички бывают проворными.
""", reply_markup=next_button)

        await RecruiterRegistry.next()
    else:
        await message.answer("Нажмите ДАЛЕЕ, чтобы продолжить обучение.")


@dp.message_handler(state=RecruiterRegistry.text3)
async def third_text(message: types.Message, state: FSMContext):
    if message.text == "ДАЛЕЕ":
        await message.answer("""Прежде, чем направить кандидата на рассмотрение рекрутер использует три проверенных шага:
        
- первичное интервью. Свяжитесь с кандидатом по аудиосвязи, чтобы задать несколько вопросов в рамках заявки. 
Прежде, выпишите себе вопросы, которые будете задавать.

- проведите видеовстречу. Используйте любую платформу для видеоконференций, например, вы можете воспользоваться видео-звонком в telegram или сейчас очень популярен zoom. 
Оцените для себя кандидата и попробуйте понять понравится ли он будущему работодателю.

- есть возможность встретиться – пригласите в кафе или к себе в офис. Разговор лучше переписки, встреча вживую - лучше общения онлайн.
Поняли, что сами взяли бы такого сотрудника к себе – направляйте работодателю на оценку и дальнейшее решение по трудоустройству.

""", reply_markup=next_button)

        await RecruiterRegistry.next()
    else:
        await message.answer("Нажмите ДАЛЕЕ, чтобы продолжить обучение.")


@dp.message_handler(state=RecruiterRegistry.text4)
async def fourth_text(message: types.Message, state: FSMContext):
    if message.text == "ДАЛЕЕ":
        await message.answer("""Перечислю вам самые популярные инструменты для проведения онлайн встреч:

- Сам телеграм 
- zoom.us 
- meet.google.com 
- telemost.yandex.ru

Используйте любой из перечисленных или иные для быстрых и качественных встреч с соискателями.
""", reply_markup=next_button)

        await RecruiterRegistry.next()
    else:
        await message.answer("Нажмите ДАЛЕЕ, чтобы продолжить обучение.")


@dp.message_handler(state=RecruiterRegistry.text5)
async def fourth_text(message: types.Message, state: FSMContext):
    if message.text == "ДАЛЕЕ":
        await message.answer(""" 
Если ты еще никак не оформил свою деятельность, для уплаты налогов, то для закрытия заявок с получением оплаты по завершнению, тебе нужно открыть самозанятость. 

Это не сложно и не потребует от тебя никаких затрат. Наоборот, позволит работать уверенно. 

Инструкция по открытию самозанятости npd.nalog.ru.

Для подтверждения ИП или самозанятости используйте команду /confirm_docs
И приложите свидетельство о регистрации ИП или справку о самозанятости.
Повышение на следующие уровни производится автоматически.
""", reply_markup=star_test_button)
        await message.answer("""Сейчас я дам вам небольшой тест.""")
        await RecruiterRegistry.next()
    else:
        await message.answer("Нажмите ДАЛЕЕ, чтобы продолжить обучение.")


@dp.message_handler(state=RecruiterRegistry.test1)
async def first_test(message: types.Message, state: FSMContext):
    if message.text == "НАЧАТЬ ТЕСТ":
        await message.answer("""В тестах может быть несколько вариантов ответов. 
Выберите те, которые считаете правильными, подтвердите ответ, после чего нажмите ДАЛЕЕ""")
        response = await bot.send_poll(
            message.from_user.id,
            *question1,
            allows_multiple_answers=True,
            reply_markup=next_button)
        session.add(Question(poll_id=response.poll.id, question=response.poll.question))
        session.commit()
        session.close()
        await state.finish()
    else:
        await message.answer("Нажмите НАЧАТЬ ТЕСТ, чтобы продолжить обучение.")


@dp.message_handler(state=RecruiterRegistry.test2)
async def second_test(message: types.Message, state: FSMContext):
    if message.text == "ДАЛЕЕ":
        response = await bot.send_poll(
            message.from_user.id,
            *question2,
            allows_multiple_answers=True,
            reply_markup=next_button)
        session.add(Question(poll_id=response.poll.id, question=response.poll.question))
        session.commit()
        session.close()
        await state.finish()
    else:
        await message.answer("Нажмите ДАЛЕЕ, чтобы получить следующий вопрос.")


@dp.message_handler(state=RecruiterRegistry.test3)
async def third_test(message: types.Message, state: FSMContext):
    if message.text == "ДАЛЕЕ":
        response = await bot.send_poll(
            message.from_user.id,
            *question3,
            allows_multiple_answers=True,
            reply_markup=finish_test_button)
        session.add(Question(poll_id=response.poll.id, question=response.poll.question))
        session.commit()
        session.close()
        await state.finish()
    else:
        await message.answer("Нажмите ДАЛЕЕ, чтобы получить следующий вопрос.")


@dp.message_handler(state=RecruiterRegistry.finish_test)
async def finish_test(message: types.Message, state: FSMContext):
    if message.text == "ЗАВЕРШИТЬ ТЕСТ":
        answer = session.query(Answer).filter_by(user_id=message.from_user.id).first()
        if answer.score == 3:
            await message.answer("Поздравляем, вы правильно ответили на все вопросы!")
            await message.answer("""Теперь вы можете закрывать заявки от работодателей. 
Чтобы увидеть доступные команды воспользуйтесь командой /get_vacancies""")
            await state.finish()
            recruiter = session.query(Recruiter).filter_by(user_id=message.from_user.id).first()
            recruiter.finished_educ = True
            session.commit()
            session.close()
        else:
            session.delete(answer)
            session.commit()
            session.close()
            await message.answer("""К сожалению, вы  ответили не на все вопросы правильно. 
Нажмите НАЧАТЬ ТЕСТ, чтобы пройти тест заново.""", reply_markup=star_test_button)
            await RecruiterRegistry.test1.set()
    else:
        await message.answer("Нажмите ЗАВЕРШИТЬ ТЕСТ, чтобы завершить тест.")


@dp.poll_answer_handler()
async def handle_poll_answer(quiz_answer: types.PollAnswer):
    poll_id = quiz_answer.poll_id
    answers = quiz_answer.option_ids
    user_id = quiz_answer.user.id
    question = session.query(Question).get(poll_id).question
    answer_score = get_or_create(session, Answer, user_id=user_id)
    if question == question1[0]:
        await RecruiterRegistry.test2.set()
        if answers == [0, 1, 3, 4, 5]:
            answer_score.score += 1
            session.commit()
            session.close()
        else:
            session.close()
    elif question == question2[0]:
        await RecruiterRegistry.test3.set()
        if answers == [0, 1, 2]:
            answer_score.score += 1
            session.commit()
            session.close()
        else:
            session.close()
    elif question == question3[0]:
        await RecruiterRegistry.finish_test.set()
        if 3 not in answers:
            answer_score.score += 1
            session.commit()
            session.close()
        else:
            session.close()


@dp.callback_query_handler(lambda callback_query: True)
async def handle_callback(callback_query: types.CallbackQuery):
    callback_list = callback_query.data.split()
    if callback_list[0] == "set_lvl":
        await admin_set_level(callback_query.from_user.id, *callback_list[1:])
    elif callback_list[0] == "in_work":
        vacancy_id = callback_list[1]
        recruiter_id = callback_list[2]
        vacancy = session.query(Vacancy).get(vacancy_id)
        recruiter = session.query(Recruiter).get(recruiter_id)
        vacancies_in_work = session.query(InWork).filter_by(recruiter_id=recruiter.id).all()
        len_vac = len(vacancies_in_work)
        if vacancy and recruiter:
            in_work = get_or_create(session, InWork, vacancy=vacancy, recruiter=recruiter)
            await bot.send_message(recruiter.user_id, f"""Заявка №{vacancy.id} {vacancy.name} в работе. 

Итого заявок в работе: {len_vac}

Используйте команду /in_work чтобы получить вакансии находящиеся у вас в работе""")
    elif callback_list[0] == "add_cand":
        vacancy_id = callback_list[1]
        recruiter_id = callback_list[2]
        vacancy = session.query(Vacancy).get(vacancy_id)
        recruiter = session.query(Recruiter).get(recruiter_id)
        vacancies_in_work = session.query(InWork).filter_by(recruiter_id=recruiter.id).all()
        len_vac = len(vacancies_in_work)
        if vacancy and recruiter:
            in_work = get_or_create(session, InWork, vacancy=vacancy, recruiter=recruiter)
            await bot.send_message(recruiter.user_id, f"""Заявка №{vacancy.id} {vacancy.name} в работе. 
Итого заявок в работе: {len_vac}
Используйте команду /in_work чтобы получить вакансии находящиеся у вас в работе""")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
