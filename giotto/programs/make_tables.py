from giotto.programs import GiottoProgram
from giotto.views import BasicView

def make_tables():
    from giotto import config
    Base = config.Base
    engine = config.engine
    Base.metadata.create_all(engine)
    return 'All tables created'

class MakeTables(GiottoProgram):
    """
    Program for creating the database tables for all imported models. Use this
    program internaly only. Do not hook it up through HTTP.
    """
    controllers = ('cmd', )
    model = [make_tables]
    view = BasicView