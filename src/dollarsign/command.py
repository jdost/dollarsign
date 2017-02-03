class Command(object):
    def __init__(self, path=""):
        self.binary = path

    def __or__(self, other):
        from dollarsign.composition import Composer
        return Composer.check(self) | other

    def __gt__(self, other):
        from dollarsign.composition import Composer
        return Composer.check(self) > other

    def __lt__(self, other):
        from dollarsign.composition import Composer
        return Composer.check(self) < other

    def __call__(self, *args, **kwargs):
        command = [self.binary]
        flags = kwargs.pop("flags", [])

        for flag in flags:
            if len(flag) == 1:
                command.append("-{!s}".format(flag))
            else:
                command.append("--{!s}".format(flag))

        for arg, opt in kwargs.items():
            if len(arg) == 1:
                command.append("-{!s}".format(arg))
                command.append(opt)
            else:
                command.append("--{!s}={!s}".format(arg, opt))

        for arg in args:
            command.append(str(arg))

        from dollarsign.composition import Composer
        return Composer(command=command)
