import dollarsign as sh
import code

try:
    import readline
except ImportError:
    pass
else:
    # import rlcompleter
    # readline.set_completer(rlcompleter.Completer(imported_objects).complete)
    readline.parse_and_bind("tab:complete")

code.interact('''
predefined:
    sh -> dollarsign
''', local=locals())
