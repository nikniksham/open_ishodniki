import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Queue(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'queue'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    spisok = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'<Queue> очередь {self.id}'
