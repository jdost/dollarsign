import os
import os.path


def executables_in(path):
    if not os.path.exists(path):
        return []

    executables = []

    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            executables += executables_in(os.path.join(path, file))
        elif os.access(os.path.join(path, file), os.X_OK):
            executables.append((file, os.path.join(path, file)))

    return executables
