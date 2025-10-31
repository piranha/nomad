import re

from sqlalchemy import create_engine, exc, text, __version__ as sqla_version

from nomad.engine import BaseEngine, DBError


class SAEngine(BaseEngine):
    def connect(self):
        engine = create_engine(self.url)
        return engine.connect()

    def prepare(self, statement, args, escape):
        # Get dialect name from connection's engine
        dialect_name = self.connection.engine.dialect.name
        if escape and dialect_name in ('mysql', 'pgsql', 'postgresql'):
            return text(statement.replace('%', '%%'))

        i = -1
        def replacer(old):
            nonlocal i
            i += 1
            return f':p{i}'

        # SQLAlchemy 2.0 always wants named params in text statements
        statement = re.sub(r'\?', replacer, statement)
        params = {f'p{i}': arg for i, arg in enumerate(args)}
        return text(statement).bindparams(**params)

    def query(self, statement, *args, **kwargs):
        statement = self.prepare(statement, args, escape=kwargs.pop('escape', False))
        try:
            return self.connection.execute(statement, **kwargs)
        except exc.SQLAlchemyError as e:
            raise DBError(str(e))

    begin = rollback = commit = lambda self: None

    if sqla_version > '2':
        def commit(self):
            self.connection.commit()

    def nobegin(self):
        """TODO:
        http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#setting-transaction-isolation-levels
        """
        raise Exception('Not implemented')


engine = SAEngine
