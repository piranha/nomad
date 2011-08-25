from sqlalchemy import create_engine

from nomad.engine import BaseEngine


class SAEngine(BaseEngine):
    def connect(self):
        self._connection = create_engine(self.url)

    def query(self, statement, *args, **kwargs):
        return self.connection.execute(statement, *args, **kwargs)


engine = SAEngine
