# Dollarsign

A pythonic library that tries to bring the unix command line style into python for
leveraging the built in binaries to your system shell.  Any executable that you have
in your path will get a handler from dollarsign.  The executable equivalent 
functions will be lazy and non-opinionated.

## Lazy

When you execute/define a dollarsign call, it will return an output object that will
not be evaluated until you try to access the output.  This object will still be
composable with other functions through the same unix-esque interface.  This allows
for a pseudo bridge between how you compose commands on the command line and how you
will compose them in python.

### Example

```
from dollarsign import *

bad_requests = grep("code", "/var/log/nginx/access.log") | grep(flags=["v", "e"], "[2|3][0-9][0-9]")

if bad_requests:
   count = bad_requests.stdout > wc(flags=["l"])
   print "There were {} failed requests".format(count.stdout)
```

## Unix Equivalents

Using python magic methods and supporting translation from the unix equivalent types
(such as streams) the composing object that dollarsign generates supports many of
the tools you are used to on your unix command line.

### Pipes

Using the pipe operator (the `|` in python is a bitwise or) will redirect the stdout
of the left hand command composition into the stdin for the right hand command
composition (it will actually become a single composition).  Because the execution
is lazy, you can do this across multiple definitions and conditionally expand your
composed execution.

### Redirection

Using the redirection operator (the `<` and `>` operators are comparisons in python)
you can tie in a stream like object to the stdout or stdin of the composed 
execution.  Stream like in python means things like file objects or anything that
implements the `read` and `write` methods.

### Boolean/Return code

The composed object can be evaluated as a conditional boolean in the same way that
the return code of an execution is used in the shell.  It will trigger an execution
from the lazy evaluator if you have not already.
