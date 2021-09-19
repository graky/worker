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
    salary = Column(Integer)
    finite_state = Column(Integer, default=0)

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