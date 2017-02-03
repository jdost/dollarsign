import os

from dollarsign import discovery
from dollarsign.command import Command

__all__ = []

for folder in os.environ["PATH"].split(":"):
    for name, path in discovery.executables_in(folder):
        if name in globals():
            continue

        globals()[name] = Command(path=path)
        __all__.append(name)

