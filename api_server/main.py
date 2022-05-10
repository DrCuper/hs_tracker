from fastapi import FastAPI
from pydantic import BaseModel

from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from sqlalchemy import create_engine, Table, Column, Integer, DateTime, Text, select, inspect, MetaData, TIMESTAMP, func, cast, Float
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime, timedelta

import logging
import json
import requests
import os

from bs4 import BeautifulSoup as bs

logging.basicConfig(filename='logs/api_server.log', filemode='a', 
                    format='[%(asctime)s] %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('logger')

app = FastAPI()
base = declarative_base()

URL_VERSIONS = "https://hearthstone.fandom.com/wiki/Patches"

TABLE_ARGS = {'schema': 'bg'}

DATABASE = {
    "drivername": "postgresql",
    "host": "postgres",
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
    bg_version = Column('bg_version', Text())
    b_deleted = Column('b_deleted', Integer(), default=0)
    b_editable = Column('b_editable', Integer(), default=0)

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
    bg_version: str = None
    b_deleted: int = 0
    b_editable: int = 0


engine = create_engine(URL(**DATABASE))
Session = sessionmaker(engine)

actual_bg_version = 23.2


def update_bg_version_to_actual():

    global actual_bg_version
    
    response = requests.request("GET", URL_VERSIONS)

    root = bs (response.text, 'html.parser')
    el = root.find('center')

    if el.a != None:

        patch = el.a.get('title').split(' ')[1].split('.')[:2]

        if len(patch) == 2:

            version = float(f'{patch[0]}.{patch[1]}')

            actual_bg_version = version

#update_bg_version_to_actual()


@app.post("/add_place")
async def add_place(data: salesmen_row):

    Session = sessionmaker(engine)
    session = Session()

    #update_bg_version_to_actual()

    session.add(salesmen(id_player=data.id_player, 
                         place=data.place, 
                         dt_insert=data.dt_insert,
                         bg_version=actual_bg_version))

    session.commit()

    result = ( session.query(salesmen).
                       filter(salesmen.b_deleted==0).
                       filter(salesmen.id_player==data.id_player).
                       filter(salesmen.dt_insert==data.dt_insert).
                       filter(salesmen.place==data.place).
                       count())

    return result


@app.delete("/delete_record/")
async def delete_record(id_record: int):
    
    Session = sessionmaker(engine)
    session = Session()

    result = (session.query(salesmen).
                      filter(salesmen.id_record == id_record).
                      update({'b_deleted': 1})
                      )

    session.commit()
    session.close()

    return result


@app.get("/ten_last")
async def ten_last(id_player: int):

    Session = sessionmaker(engine)   
    session = Session()

    result = (session.query(salesmen.id_record, salesmen.place, salesmen.dt_insert, salesmen.bg_version).
                      filter(salesmen.id_player==id_player).
                      filter(salesmen.b_deleted==0).
                      order_by(salesmen.id_record.desc()).
                      limit(10).
                      all()
                      )

    session.close()

    return result


@app.get("/ten_last_avg")
async def ten_last_avg(id_player: int):

    Session = sessionmaker(engine)
    session = Session()

    result = (session.query(players.v_name, func.avg(salesmen.place).label('avg')).
                      filter(salesmen.id_player==id_player).
                      filter(salesmen.b_deleted==0).
                      join(players, players.id_player==salesmen.id_player).
                      group_by(players.v_name).
                      limit(10).
                      all()
                      )

    session.close()

    return result


@app.get("/weekly_avg")
async def weekly_avg():

    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(players.v_name, func.avg(salesmen.place).label('avg')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.b_deleted==0).
                       filter(salesmen.dt_insert>=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/weekly_games")
async def weekly_games():

    Session = sessionmaker(engine)   
    session = Session()

    result = ( session.query(players.v_name, func.count(salesmen.place).label('count')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.b_deleted==0).
                       filter(salesmen.dt_insert>=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/weekly_place")
async def weekly_place(place: int):

    Session = sessionmaker(engine) 
    session = Session()

    result = ( session.query(players.v_name, func.count(salesmen.place).label('count')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.place==place).
                       filter(salesmen.b_deleted==0).
                       filter(salesmen.dt_insert>=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/total_top_place")
async def total_top_place(place: int):
    
    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(players.v_name, func.count(salesmen.place).label('count')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.place==place).
                       filter(salesmen.b_deleted==0).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/total_avg")
async def total_avg():

    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(players.v_name, func.avg(salesmen.place).label('avg')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.b_deleted==0).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/total_avg_user")
async def total_avg_user(id_player: int):

    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(players.v_name, func.avg(salesmen.place).label('avg')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.b_deleted==0).
                       filter(salesmen.id_player==id_player).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result

@app.get("/total_avg_user_per_version")
async def total_avg_user_per_version(id_player: int):

    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(players.v_name, salesmen.bg_version, func.avg(salesmen.place).label('avg')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.b_deleted==0).
                       filter(salesmen.id_player==id_player).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result


@app.get("/total_avg_per_version")
async def total_avg_per_version():

    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(players.v_name, salesmen.bg_version, func.avg(salesmen.place).label('avg')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.b_deleted==0).
                       group_by(players.v_name, salesmen.bg_version).
                       all()
                       )

    session.close()

    return result


@app.get("/total_period")
async def total_period(place: int):
    
    Session = sessionmaker(engine)
    session = Session()

    subresult = ( session.query(func.count(salesmen.place).label("cnt"), salesmen.id_player).
                       filter(salesmen.place==place).
                       filter(salesmen.b_deleted==0).
                       group_by(salesmen.id_player).
                       subquery()
                       )

    result = ( session.query(players.v_name, (cast(func.count(salesmen.place), Float(2,2)) / subresult.c.cnt).label('count')).
                       select_from(subresult).
                       join(players, players.id_player==subresult.c.id_player).
                       join(salesmen, salesmen.id_player==subresult.c.id_player).
                       filter(salesmen.b_deleted==0).
                       group_by(players.v_name, subresult.c.cnt).
                       all()
                       )

    session.close()

    return result


@app.get("/total_games")
async def total_games():

    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(players.v_name, func.count(salesmen.place).label('count')).
                       join(players, players.id_player==salesmen.id_player).
                       filter(salesmen.b_deleted==0).
                       group_by(players.v_name).
                       all()
                       )

    session.close()

    return result

@app.get("/bg_version")
async def bg_version():

    response = requests.request("GET", URL_VERSIONS)

    root = bs (response.text, 'html.parser')
    el = root.find('center')

    if el.a != None:

        patch = el.a.get('title').split(' ')[1].split('.')[:2]

        if len(patch) == 2:

            version = float(f'{patch[0]}.{patch[1]}')

    return { 'version': version}


@app.get("/bg_version_all")
async def bg_version_all():

    Session = sessionmaker(engine)
    session = Session()

    result = ( session.query(salesmen.bg_version).
                       distinct().
                       all()
    )

    session.close()

    return result


@app.put("/bg_version_update_all")
async def bg_version_update_all():

    patches = []

    response = requests.request("GET", URL_VERSIONS)

    root = bs (response.text, 'html.parser')
    el = root.find('center')
    trs = el.find_all('tr')

    for line in trs[::-1]:

        href = line.a

        date = line.find_all('td')

        if href != None:

            patch = href.get('title').split(' ')[1].split('.')[:2]

            if len(patch) == 2:

                patches.append({'version': float(f'{patch[0]}.{patch[1]}'), 'date': str(date[2]).split('>')[1].split('<')[0]})


    for dt in patches:

        Session = sessionmaker(engine)
        session = Session()

        print(dt)
        (session.query(salesmen).
                 filter(salesmen.dt_insert > dt.get('date')).
                 filter(salesmen.b_editable == 1).
                 update({'bg_version': dt.get('version')}))

        session.commit()
        session.close()

    return patches

def make_all_ids_normal():

    nmbs = []

    Session = sessionmaker(engine)
    session = Session()

    result = session.query(salesmen.id_record).order_by(salesmen.id_record)

    session.close()

    for number in result:

        nmbs.append(number[0])

    nmbs.sort()

    for i in range(1,len(nmbs) + 1):

        Session = sessionmaker(engine)
        session = Session()

        result = (session.query(salesmen).
                        filter(salesmen.id_record == nmbs[i - 1]).
                        update({'id_record': i})
                        )

        session.commit()
        session.close() 

make_all_ids_normal()