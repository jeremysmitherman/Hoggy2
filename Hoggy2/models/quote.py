from sqlalchemy import Column, Integer, String, Text
from random import randint
import Hoggy2.meta as meta

class Quote(meta.base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True)
    body = Column(Text)

    @classmethod
    def get_quote(cls, id = None):
        try:
            if id is None:
                return meta.session.query(cls).order_by(func.random()).one()
            return meta.session.query(cls).get(id)
        except:
            meta.session.rollback()
            raise

    @classmethod
    def add_quote(cls, quote):
        try:
            new_quote = cls()
            new_quote.body = quote
            meta.session.add(new_quote)
            meta.session.commit()

            return new_quote.id
        except:
            meta.session.rollback()
            raise

    def delete(self):
        try:
            meta.session.delete(self)
            meta.session.commit()
        except:
            meta.session.rollback()
            raise
