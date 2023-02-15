from datetime import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Logs(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'logs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_tel_id = sqlalchemy.Column(sqlalchemy.String)
    action = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())

    def __repr__(self):
        return f'<Log> {self.action} в {self.formatted_date()}'

    def formatted_date(self):
        d = self.created_date
        return f"{str(d.year).rjust(2, '0')}.{str(d.month).rjust(2, '0')}.{d.day} {str(d.hour).rjust(2, '0')}:{str(d.minute).rjust(2, '0')}"
