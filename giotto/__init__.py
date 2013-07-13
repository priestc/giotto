__version__ = '0.11.0'

def initialize(config, secrets, machine):
    import giotto
    setattr(giotto, '_config', config)

    for item in dir(secrets):
        s_value = getattr(secrets, item)
        setattr(giotto._config, item, s_value)

    for item in dir(machine):
        s_value = getattr(machine, item)
        setattr(giotto._config, item, s_value)

def get_config(item, default=None):
    """
    Use this functio to get values from the config object.
    """
    import giotto
    return getattr(giotto._config, item, default) or default