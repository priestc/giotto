from sqlalchemy import Column, String, Integer
from giotto import get_confg
Base = get_confg('Base')

class Message(Base):
    message = Column(String)
    level = Column(Integer)

    user_id = Column(Integer, ForeignKey('giotto_user.username'))
    user = relationship("User", backref=backref('messages', order_by=id))

    @classmethod
    def get(cls, user):
        return config.session.query(cls).filter(user=user).all()

    @classmethod
    def info(cls, user, message):
        return _make_message(user, message, level=1)

    @classmethod
    def debug(cls, user, message):
        return _make_message(user, message, level=2)

    @classmethod
    def error(cls, user, message):
        return _make_message(user, message, level=3)

    @classmethod
    def fatal(cls, user, message):
        return _make_message(user, message, level=4)

    @classmethod
    def _make_message(user, message, level):
        msg = cls(user=user, level=level)
        config.session.add(msg)
        config.session.commit()