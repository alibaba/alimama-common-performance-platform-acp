# _*_coding:utf-8_*_
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AcpTask(Base):
    __tablename__ = 'acp_task'

    id = Column(Integer, primary_key=True)
    timestamp = Column(String(128))
    taskid = Column(String(128))
    acpid = Column(String(128))
    target = Column(String(128))
    query = Column(String(128))
    qps = Column(String(128))
    protocol = Column(String(128))
    source = Column(String(128))
    option_str = Column(String(128))
    owner = Column(String(128))
    json_conf = Column(String(25600))
