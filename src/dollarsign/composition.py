import os
import subprocess

from dollarsign.command import Command


class Process(object):
    ''' composition::Process
    Lower level wrapper around the subprocess composition and calling.  Meant
    to be manipulated by the ::Composer class for chaining and modifying the
    process streams.  (NOTE: this is a work around to the fact that
    `subprocess.Popen` executes upon construction and in order for these to be
    lazy, that is not desired)
    '''
    def __init__(self, command):
        ''' (constructor)
        Initializes the command to be run into a clean array of strings and
        prepares the streams and subprocess attribute so that they can be
        modified/accessed.
        '''
        if isinstance(command, list):
            self.command = [str(c) for c in command]
        else:
            self.command = [str(command)]

        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.process = None

    def __call__(self, **kwargs):
        ''' (executor)
        Generates a subprocess Popen execution that mirrors the constructed
        and configured format of this Process object.
        '''
        self.process = subprocess.Popen(
            self.command,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.stderr,
            **kwargs
        )

        return self

    def wait(self):
        ''' wait
        Will stall the code execution until the subprocess is finished running
        (if there is a process) otherwise will just return `None`.
        '''
        return self.process.wait() if self.process else None


class Composer(object):
    ''' composition::Composer
    Intelligent command chain composition instance.  A composer starts off with
    a single base command and can be built up to a larger command chain using
    pipe redirection and input/output redirection into file-like objects.

    Uses property wrappers to allow for lazy evaluation when the properties are
    accessed and not upon definition.
    '''

    @classmethod
    def check(cls, obj):
        ''' Composer::check
        Checks/coerces the passed in `obj` into a Composer object, if possible,
        otherwise raises a TypeError.
        '''
        if isinstance(obj, Command):
            return obj()
        elif not isinstance(obj, cls):
            raise TypeError

        return obj

    def __init__(self, command=[]):
        ''' (constructor)
        Builds an initial Composer object with the passed in command list as
        the base process.
        '''
        self.commands = [Process(command)]

        self.return_code = None
        self.streams = {}

    def __run_check__(self):
        ''' (private) __run_check__
        Helper method to check if the lazy evaluation has been run and runs it
        if it has not.
        '''
        if self.return_code is None:
            self.__execute__()

    @property
    def stdout(self):
        ''' (getter) stdout
        Lazy wrapper for the stdout stream of the overall composition chain.
        Will execute the process chain if it has not been run, provides the
        stdout for the end process in the chain.
        '''
        self.__run_check__()
        return self.streams.get("stdout", "")

    @property
    def stderr(self):
        ''' (getter) stderr
        Lazy wrapper for the stderr stream of the overall composition chain.
        Will execute the process chain if it has not been run, provides the
        stderr for the end process in the chain.
        '''
        self.__run_check__()
        return self.streams["stderr"]

    @property
    def stdin(self):
        ''' (getter) stdin
        Intelligent getter for the stdin stream.  Because stdin only matters
        during the execution of the process chain, an error will be raised if
        the process chain has already been executed, otherwise will attempt to
        provide the predefined stdin stream.
        '''
        if self.return_code is not None:
            raise "The stdin for this is closed"

        return self.streams.get("stdin")

    @stdin.setter
    def set_stdin(self, buffer):
        ''' (setter) stdin
        Intelligent setter for the stdin stream.  If the process chain has
        already been executed, an error will be raised, otherwise the stdin
        stream for the root (first process in the chain) will be set to the
        stream provided.
        '''
        if self.return_code is not None:
            raise "The stdin for this is closed"

        self.commands[0].stdin = buffer
        self.streams["stdin"] = buffer

    def __call__(self, **kwargs):
        ''' (executor)
        Aliases the internal `__execute__` method to make the object callable
        '''
        return self.__execute__(**kwargs)

    def __execute__(self, **kwargs):
        ''' (private) __execute__
        Implements the execution strategy for the configured process chain.
        Will go through the chained commands in order and execute the
        subprocess and then wait until each is finished and tidy up the stream
        objects and update the attributes for the object to reflect the
        outcome of the process chain.
        '''
        procs = []
        for command in self.commands:
            procs.append(command(**kwargs))

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
        ''' (string representation)
        Builds the shell equivalent of the command chain
        '''
        return " | ".join([" ".join(cmd.command) for cmd in self.commands])

    def __repr__(self):
        ''' (code representation)
        Shows the shell equivalent of the command chain in a reference format
        for the library.
        '''
        return "<sh: $ {!s}>".format(self)

    def __nonzero__(self):
        ''' (boolean representation)
        Returns a boolean value for whether the process chain executed
        successfully.  This is interpreted as an exit code of zero for the
        final process in the chain.  This is confusing with the name but is
        meant to reflect how the shell interprets truthiness.
        '''
        self.__run_check__()
        return self.return_code == 0

    def __int__(self):
        ''' (integer representation)
        Returns the exit code for the final process in the chain.
        '''
        self.__run_check__()
        return self.return_code

    def __or__(self, other):
        ''' (bitwise or operator)
        Overrides the idea of a bitwise operator (the single pipe) to allow for
        chaining two commands together.  The chaining follows the unix
        convention by tying the stdout of the previous command into the stdin
        of the next command.  The new command(s) are then appended to the
        overall composition chain.
        '''
        other = Composer.check(other)

        tail = self.commands[-1]
        head = other.commands[0]

        head.stdin, tail.stdout = build_stream()

        self.commands += other.commands

        return self

    def __gt__(self, other):
        ''' (greater than comparator)
        Overrides the idea of a greater than comparison to allow for output
        redirection.  If the passed in object is a writable file-like object,
        it will be tied to the stdout of the final command in the chain.
        '''
        if not hasattr(other, 'write'):
            raise TypeError

        self.commands[-1].stdout = other
        return self

    def __lt__(self, other):
        ''' (less than comparator)
        Overrides the idea of a less than comparison to allow for input
        redirection.  If the passed in object is a readable file-like object,
        it will be tied to the stdin of the base command in the chain.
        '''
        if not hasattr(other, 'read'):
            raise TypeError

        self.commands[0].stdin = other
        return self

    def __enter__(self):
        ''' (context wrapper entry)
        Allows for the composition to be done in a context manager and then
        executed at the end of the context block.
        '''
        return self

    def __exit__(self, ex_type, ex_val, trace):
        ''' (context wrapper exit)
        If the context block finished without exception, attempts to execute
        the finished context block.
        '''
        if ex_type is None:
            return self.__execute__()


def build_stream():
    ''' build_stream
    Returns a pair of OS file descriptors for a data stream.  The first is the
    output half of the stream and allows reading only.  The second is the input
    half of the stream and allows writing only.  The input in the second half
    will be the output of the first half.  This is used to create OS compliant
    I/O redirection between chained processes.
    '''
    return os.pipe()
