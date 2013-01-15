__version__ = '0.10.4'

def initialize(config):
    import giotto
    setattr(giotto, '_config', config)

def get_config(item, default=None):
    import giotto
    return getattr(giotto._config, item, default)