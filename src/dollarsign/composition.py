import os
import subprocess

from dollarsign.command import Command


class Process(object):
    def __init__(self, command):
        if isinstance(command, list):
            self.command = [str(c) for c in command]
        else:
            self.command = [str(command)]

        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.process = None

    def __call__(self):
        self.process = subprocess.Popen(
            self.command,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.stderr
        )

        return self

    def wait(self):
        return self.process.wait() if self.process else None


class Composer(object):
    @classmethod
    def check(cls, obj):
        if isinstance(obj, Command):
            return obj()
        elif not isinstance(obj, cls):
            raise TypeError

        return obj

    def __init__(self, command=[]):
        self.commands = [Process(command)]

        self.return_code = None
        self.streams = {}

    def __run_check__(self):
        if self.return_code is None:
            self.__execute__()

    @property
    def stdout(self):
        self.__run_check__()
        return self.streams["stdout"]

    @property
    def stderr(self):
        self.__run_check__()
        return self.streams["stderr"]

    @property
    def stdin(self):
        if self.return_code is not None:
            raise "The stdin for this is closed"

        return self.streams.get("stdin")

    @stdin.setter
    def set_stdin(self, buffer):
        if self.return_code is not None:
            raise "The stdin for this is closed"

        self.commands[0].stdin = buffer
        self.streams["stdin"] = buffer

    def __call__(self):
        return self.__execute__()

    def __execute__(self):
        procs = []
        for command in self.commands:
            procs.append(command())

        for proc in procs:
            if isinstance(proc.stdin, int):
                os.close(proc.stdin)
            elif hasattr(proc.stdin, 'close'):
                proc.stdin.close()

            self.return_code = proc.wait()

            if isinstance(proc.stdout, int):
                os.close(proc.stdout)
            elif hasattr(proc.stdout, 'close'):
                proc.stdout.close()

        self.streams["stdout"] = proc.stdout
        self.streams["stderr"] = proc.stderr

        return self.streams["stdout"]

    def __str__(self):
        return " | ".join([" ".join(cmd.command) for cmd in self.commands])

    def __repr__(self):
        return "<sh: $ {!s}>".format(self)

    def __nonzero__(self):  # this is confusing, in unix, a 0 exit code is true
        self.__run_check__()
        return self.return_code == 0

    def __int__(self):
        self.__run_check__()
        return self.return_code

    def __or__(self, other):
        other = Composer.check(other)

        tail = self.commands[-1]
        head = other.commands[0]

        head.stdin, tail.stdout = build_stream()

        self.commands += other.commands

        return self

    def __gt__(self, other):
        if not hasattr(other, 'write'):
            raise TypeError

        self.commands[-1].stdout = other
        return self

    def __lt__(self, other):
        if not hasattr(other, 'read'):
            raise TypeError

        self.commands[0].stdin = other
        return self

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_val, trace):
        if ex_type is None:
            return self.__execute__()


def build_stream():
    return os.pipe()
