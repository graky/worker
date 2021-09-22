from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import random
import os
from os import environ

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    telegram_id = Column(Integer, primary_key=True)
    employer = relationship("Employer", back_populates="user")
    recruiter = relationship("Recruiter", back_populates="user")


class Employer(Base):
    __tablename__ = 'employer'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.telegram_id'))
    user = relationship("User", back_populates="employer")
    vacancies = relationship("Vacancy")


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    employer_id = Column(Integer, ForeignKey('employer.id'))
    employer = relationship("Employer", back_populates="vacancies")
    company = Column(String)
    website = Column(String)
    name = Column(String)
    duties = Column(String)
    requirements = Column(String)
    conditions = Column(String)
    pay_level = Column(String)
    numb_level = Column(Integer)
    salary = Column(Integer)
    finite_state = Column(Integer, default=0)
    active = Column(Boolean, default=False)

    def __repr__(self):
        form = """
Заявка на подбор персонала : {0}

Компания: {1} {2}

Наименование вакансии: {3}

Обязанности: {4}

Требования:

{5}

Условия:

{6}

Уровень вознаграждения за подбор: {7}

Сумма вознаграждения: {8}
"""
        form = form.format(
            self.id,
            self.company,
            self.website,
            self.name,
            self.duties,
            self.requirements,
            self.conditions,
            self.pay_level,
            self.salary)
        return form


class Recruiter(Base):
    __tablename__ = 'recruiter'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.telegram_id'))
    user = relationship("User", back_populates="recruiter")
    level = Column(String)
    level_numb = Column(Integer)
    resume = relationship("Resume", back_populates="recruiter")


class Resume(Base):
    __tablename__ = "resume"
    id = Column(Integer, primary_key=True)
    recruiter_id = Column(Integer, ForeignKey('recruiter.id'))
    recruiter = relationship("Recruiter", back_populates="resume")
    fio = Column(String)
    years = Column(String)
    specialization = Column(String)
    tools = Column(String)
    difficulties = Column(String)
    invitation = Column(String)
    letter = Column(String)
    refusal = Column(String)

    def __repr__(self):
        resume = """
- Ваше ФИО\n
{0}\n
- Сколько лет вы в подборе\n
{1}\n
- В какой области вы специализируетесь\n
{2}\n
- Какими инструментами пользуетесь при подборе\n
{3}\n
- С какими трудностями сталкивались при подборе\n
{4}\n
- Напишите краткое приглашение соискателю на вакансию\n
{5}\n
- Вы не можете долго закрыть заявку и понимаете, что заработная плата не в рынке. Напишите письмо работодателю с предложением откорректировать заявку.\n
{6}\n
- Не все соискатели подошли. Как вы откажете соискателю\n
{7} \n
"""
        resume = resume.format(
            self.fio,
            self.years,
            self.specialization,
            self.tools,
            self.difficulties,
            self.invitation,
            self.letter,
            self.refusal,
        )
        return resume

user = "postgre"
password = "postgre"
db_name = "bot"
db_host = "localhost"
engine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (str(user), str(password), str(db_host), str(db_name)))
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
DBSession.bind = engine
session = DBSession()