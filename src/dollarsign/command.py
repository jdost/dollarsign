import os.path


class Command(object):
    ''' command::Command
    Wrapper for construction of a composition chain from a predefined binary
    file.
    '''
    def __init__(self, path=""):
        ''' (constructor)
        Sets the binary that this object is wrapping
        '''
        self.binary = path
        self.short_binary = os.path.basename(path)

    def __str__(self):
        return self.binary

    def __repr__(self):
        return "<sh: $ {}>".format(self.short_binary)

    def __or__(self, other):
        ''' (bitwise or override)
        Generates a new composition::Composer chain with the binary path as
        the root and uses the bitwise or/pipe definition in composition.
        '''
        from dollarsign.composition import Composer
        return Composer.check(self) | other

    def __gt__(self, other):
        ''' (greater than comparitor)
        Generates a new composition::Composer chain with the binary path as
        the root and uses the comparator definition in composition.
        '''
        from dollarsign.composition import Composer
        return Composer.check(self) > other

    def __lt__(self, other):
        ''' (less than comparitor)
        Generates a new composition::Composer chain with the binary path as
        the root and uses the comparator definition in composition.
        '''
        from dollarsign.composition import Composer
        return Composer.check(self) < other

    def __call__(self, *args, **kwargs):
        ''' (executor)
        Takes an open ended listing of arguments and formulates the resulting
        command to be passed into the composition::Composer chain builder.

        All kwargs are considered flags with an attribute and if there is a
        `flags` kwargs, it is considered a list of flags without attributes.
        If an option flag is a single character, it is prefixed with a single
        dash, if it is multiple characters, two dashes are used.
        '''
        command = [self.binary]

        for flag in kwargs.pop("flags", []):
            command.append(
                ("-{!s}" if len(flag) == 1 else "--{!s}").format(flag))

        for arg, opt in kwargs.items():
            command.append(
                ("-{!s} {!s}" if len(flag) == 1 else "--{!s}={!s}").format(flag))

        for arg in args:
            command.append(str(arg))

        from dollarsign.composition import Composer
        return Composer(command=command)
