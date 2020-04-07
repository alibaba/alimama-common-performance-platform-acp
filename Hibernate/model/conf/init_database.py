import MySQLdb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import settings

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None
    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance

class Session(object):
    #__metaclass__ = Singleton

    def __init__(self):
        conn = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (settings.DB_USER,settings.DB_PASS,settings.MYSQL_HOST,settings.MYSQL_PORT,settings.DB_NAME)
        engine = create_engine(conn)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def query(self,*args, **kw):
        return self.session.query(*args, **kw)

    def commit(self):
        self.session.commit()

    def add(self,model):
        self.session.add(model)
        self.commit()

    def __del__(self):
        self.session.close()

session = Session()
if __name__ == '__main__':
    print "fa" 
