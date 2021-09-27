import logging
from models import Base, User, Employer, Vacancy, Recruiter, Resume, Question, Answer
from models import get_or_create
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from random import choice
import random
user = "postgre"
password = "postgre"
db_name = "bot"
db_host = "localhost"
engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (str(user), str(password), str(db_host), str(db_name)))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
DBSession.bind = engine
session = DBSession()



session.add(User(telegram_id=228))
session.add(Employer(user_id=228))
employer = session.query(Employer).first()
pay_level_dict = {
    'LIGHT': [[1, 500], 1],
    'MEDIUM': [[501, 5000], 2],
    'HARD': [[5001, 10000], 3],
    'PRO': [[10001, 10000000], 4]
}

for i in range(69):
    random_lvl = choice(list(pay_level_dict.keys()))

    session.add(Vacancy(employer=employer, company= "Тестовая компания", website="pornhub.com", name=f"dungeon master {i}", duties=f"spanking {i}", requirements= f"college boy {i}",
                        conditions=f"gym {i}",
                       pay_level= random_lvl, numb_level=pay_level_dict[random_lvl][1], salary=random.randrange(pay_level_dict[random_lvl][0][0], pay_level_dict[random_lvl][0][1]),
                        finite_state=10, active=True) )
    session.commit()
session.close()
