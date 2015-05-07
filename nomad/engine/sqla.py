import re

from sqlalchemy import create_engine, exc

from nomad.engine import BaseEngine, DBError


class SAEngine(BaseEngine):
    def connect(self):
        return create_engine(self.url)

    def prepare(self, statement):
        if self.connection.name in ('mysql', 'pgsql', 'postgresql'):
            return statement.replace('?', '%s')
        return statement

    def query(self, statement, *args, **kwargs):
        if not kwargs.pop('no_prepare', False):
            statement = self.prepare(statement)
        try:
            return self.connection.execute(statement, *args, **kwargs)
        except exc.SQLAlchemyError as e:
            raise DBError(str(e))

    begin = rollback = commit = lambda self: None


engine = SAEngine
