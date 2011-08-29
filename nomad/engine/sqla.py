from sqlalchemy import create_engine, exc

from nomad.engine import BaseEngine, DBError


class SAEngine(BaseEngine):
    def connect(self):
        self._connection = create_engine(self.url)

    def query(self, *args, **kwargs):
        try:
            return self.connection.execute(*args, **kwargs)
        except exc.SQLAlchemyError, e:
            raise DBError(str(e))

    begin = rollback = commit = lambda self: None


engine = SAEngine
