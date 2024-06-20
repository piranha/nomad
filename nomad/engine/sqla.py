from sqlalchemy import create_engine, exc

from nomad.engine import BaseEngine, DBError


class SAEngine(BaseEngine):
    def connect(self):
        return create_engine(self.url)

    def set_isolation_level(self, isolation_level):
        """TODO:
        http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#setting-transaction-isolation-levels
        """

    def prepare(self, statement, escape):
        if self.connection.name in ('mysql', 'pgsql', 'postgresql'):
            if escape:
                return statement.replace('%', '%%')
            return statement.replace('?', '%s')
        return statement

    def query(self, statement, *args, **kwargs):
        statement = self.prepare(statement, kwargs.pop('escape', False))
        try:
            return self.connection.execute(statement, *args, **kwargs)
        except exc.SQLAlchemyError as e:
            raise DBError(str(e))

    begin = rollback = commit = lambda self: None

    def nobegin(self):
        """TODO:
        http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#setting-transaction-isolation-levels
        """
        raise Exception('Not implemented')


engine = SAEngine
