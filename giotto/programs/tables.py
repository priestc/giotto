import six

def make_tables():
    """
    Create all the tables for the models that have been added to the manifest.
    """
    from giotto import config
    engine = config.engine
    config.Base.metadata.create_all(engine)
    print('Creating tables...')
    for i, t in enumerate(config.Base.metadata.tables.keys()):
        print(t)
    return '%s tables created' % (i + 1)

def blast_tables():
    """
    Drop all existing tables in the database, and then recreate them.
    """
    msg = "This will delete all data in your tables, are you sure? [yN]"
    if six.PY3:
        yn = input(msg)
    else:
        yn = raw_input(msg)
    if yn.lower() != 'y':
        return "Aborting"
    from giotto import config
    config.Base.metadata.drop_all(config.engine)
    print("blasting away all tables...")
    return make_tables()