from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
import server_config

url = URL.create(
    drivername="mysql+pymysql",
    username=server_config.MYSQL_EVENTS_USER,
    password=server_config.MYSQL_EVENTS_PASSWORD,
    host="172.17.89.147", # TODO: change to env var?
    database="events",
    port=3306
)
engine = create_engine(url, echo=True)
Session = sessionmaker(bind=engine)
session = Session()