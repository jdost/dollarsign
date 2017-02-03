import os
import os.path


def executables_in(path):
    ''' executables_in
    Generates a list of all of the executable files from a walking of the
    provided path.
    '''
    if not os.path.exists(path):
        return []

    executables = []

    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            executables += executables_in(os.path.join(path, file))
        elif os.access(os.path.join(path, file), os.X_OK):
            executables.append((file, os.path.join(path, file)))

    return executables
