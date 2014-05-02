from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import Hoggy2

if Hoggy2.config.get('hoggy', 'dbtype') == 'mysql':
    MSQLUname = Hoggy2.config.get('hoggy', 'mysqlusername')
    MSQLPW = Hoggy2.config.get('hoggy', 'mysqlpassword')
    MSQLHost = Hoggy2.config.get('hoggy', 'mysqlhost')
    MSQLPort = Hoggy2.config.get('hoggy', 'mysqlport')
    MSQLDB = Hoggy2.config.get('hoggy', 'mysqldatabase')
    engine = create_engine('mysql://%s:%s@%s:%s/%s' % (MSQLUname, MSQLPW, MSQLHost, MSQLPort, MSQLDB))
else:
    SQLITEFILE = Hoggy2.config.get('hoggy', 'dbfile') 
    engine = create_engine('sqlite:///%s' % SQLITEFILE,connect_args={'check_same_thread':False})



Session = sessionmaker(bind=engine)
session = Session()
base = declarative_base()
