import Hoggy2.meta as meta
from sqlalchemy import Column, Integer, String, Text, Float

class Time(meta.base):
    __tablename__ = "times"
    name = Column(String, primary_key=True)
    time = Column(Float)

    @classmethod
    def get_by_name(cls, name):
        try:
            return meta.session.query(cls).filter_by(name=name).one()
        except:
            return None

    def save(self):
        meta.session.add(self)
        meta.session.commit()