import os

def shell(shell=''):
    from giotto import config
    
    if shell == "bpython" or shell == 'b':
        import bpython
        bpython.embed()
        return

    elif shell == 'ipython' or shell == 'i':
        from IPython import embed
        embed()
        return

    else:
        import code
        imported_objects = {'config': config}
        try:  # Try activating rlcompleter, because it's handy.
            import readline
        except ImportError:
            pass
        else:
            # We don't have to wrap the following import in a 'try', because
            # we already know 'readline' was imported successfully.
            import rlcompleter
            readline.set_completer(rlcompleter.Completer(imported_objects).complete)
            readline.parse_and_bind("tab:complete")

        # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
        # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
        for pythonrc in (os.environ.get("PYTHONSTARTUP"),
                         os.path.expanduser('~/.pythonrc.py')):
            if pythonrc and os.path.isfile(pythonrc):
                try:
                    with open(pythonrc) as handle:
                        exec(compile(handle.read(), pythonrc, 'exec'))
                except NameError:
                    pass
        code.interact(local=imported_objects)

    return