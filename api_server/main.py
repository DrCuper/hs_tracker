from fastapi import FastAPI
from pydantic import BaseModel

from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from sqlalchemy import create_engine, Table, Column, Integer, DateTime, Text, select, inspect, MetaData, TIMESTAMP, func
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime, timedelta

import logging
import json
import requests
import subprocess
import os

logging.basicConfig(filename='api_server.log', filemode='a', 
                    format='[%(asctime)s] %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('logger')

app = FastAPI()
base = declarative_base()

TABLE_ARGS = {'schema': 'bg'}

DATABASE = {
    "drivername": "postgres",
    "host": "localhost",
    "port": "5432",
    "username": "dr",
    "password": "azxswq1e",
    "database": "dr"
    }

class salesmen(base):  

    __tablename__ = 'salesmen'

    id_record = Column('id_record', Integer(), primary_key=True)
    id_player = Column('id_player', Integer())
    place = Column('place', Integer())
    dt_insert = Column('dt_insert', Text(), default=datetime.now)

    __table_args__ = TABLE_ARGS


class players(base):

    __tablename__ = 'players'

    id_player = Column('id_player', Integer(), primary_key=True)
    v_name = Column('v_name', Text())

    __table_args__ = TABLE_ARGS


class salesmen_row(BaseModel):

    id_record: int = None
    id_player: int = None
    place: int = None
    dt_insert: str = None


engine = create_engine(URL(**DATABASE))
Session = sessionmaker(engine)


@app.post("/add_place")
async def add_place(data: salesmen_row):

    session = Session()

    result = session.add(salesmen(id_player=data.id_player, 
                                  place=data.place, 
                                  dt_insert=data.dt_insert))

    session.commit()
    session.close()

    return result


@app.delete("/delete_record")
async def delete_record(data: salesmen_row):
    
    session = Session()

    result = (session.query(salesmen).
                      filter(salesmen.id_record == data.id_record).
                      delete()
                      )

    session.commit()
    session.close()

    return result


@app.get("/ten_last")
async def ten_last(data: salesmen_row):
    
    session = Session()

    result = (session.query(salesmen).
                      filter(salesmen.id_player==data.id_player).
                      order_by(salesmen.id_record.desc()).
                      limit(10).
                      all()
                      )

    session.close()

    return result


@app.get("/ten_last_avg")
async def ten_last_avg(data: salesmen_row):

    session = Session()

    result = (session.query(func.avg(salesmen.place)).
                      filter(salesmen.id_player==data.id_player).
                      group_by(salesmen.id_player).
                      limit(10).
                      all()
                      )

    session.close()

    return result


#todo
'''
- weekly ratings ( place, avg, games)
- rating top-1
- rating avg place
- rating period place
- antirating
- total games
'''
@app.get("/weekly_avg")
async def weekly_avg():

    session = Session()

    result = ( session.query(players.v_name, func.avg(salesmen.place)).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.dt_insert>=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/weekly_games")
async def weekly_games():
    
    session = Session()

    result = ( session.query(players.v_name, func.count(salesmen.place)).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.dt_insert>=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/weekly_place")
async def weekly_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass


@app.post("/add_place")
async def add_place(data: dict):
    pass
     


