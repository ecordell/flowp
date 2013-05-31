from flowp import ftypes
import subprocess
import os
import shutil
import subprocess


class Process(ftypes.Object):
    """Manage structure of process / command
    Example:
        
        p = Process('./some/script')
        p.arg('--test1', 1)
        p.arg('--test2', ['a', 'b'])
        p.arg('test3')
        p.command # -> ./some/script --test1 1 --test2 a b test3
        p.run()
    """
    def __init__(self, process_name):
        """Create base of command structure as list"""
        self.elements = ftypes.List([process_name])

    def arg(self, kv, v=None):
        """Add arguments to the process
        :param kv:
            argument key/name or value right away
        :param v:
            argument value. It can be list/tuple or
            single value object.
        """
        def func(item):
            if item.isinstance(tuple) and item.len and item[0] == kv:
                return (kv, v)
            else:
                return item

        if v:
            if self.elements.filter(
                    lambda el: el.isinstance(tuple) and el[0] == kv):
                self.elements.map_it(func)
            else:
                self.elements.append((kv, v))
        else:
            self.elements.append(kv) 

    @property
    def command(self):
        """Return constructed command as string
        :rtype str:
        """
        return self.elements.flatten.flatten.join(' ')

    def run(self):
        """Run constructed command as process"""
        def func(item):
            if item.isinstance(str):
                return item
            else:
                return item.str

        subprocess.check_call(self.elements.flatten.map(func))


class cd:
    """Change working directory. Behave exacly like os.chdir, except
    that it can be used as context manager.
    Example:

        with cd('some/path'):
            # do some operations
            pass

    After exiting the context, return to the oryginal working directory.
    This also works but doesn't return to the original working dir:

        cd('some/path')
    """
    def __init__(self, path):
        self.org_dir = os.getcwd()
        os.chdir(path) 

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.chdir(self.org_dir)


# Alias for shutil.move
mv = shutil.move

# Alias for os.mkdir
mkdir = os.makedirs

# Alias for os.unlink
rm = os.unlink


def sh(command):
    """Executes shell command as is
    :param str command:
        command to execute
    """ 
    subprocess.check_call(command, shell=True)


# Import alias for better debugging / mocking
import_alias = __import__


class FlowpFileExecuter(ftypes.Object):
    def __init__(self, args):
        self.args = args

    @property
    def tasks(self):
        def func(item):
            if item.len == 1:
                return [item[0], []]
            else:
                return [item[0], item[1].split(',')]

        tasks = ftypes.List(self.args[1:])
        tasks.map_it(lambda x: x.split(':'))
        tasks.map_it(func)
        return tasks.dict

    def execute(self):
        flowpfile = import_alias('flowpfile', globals(), locals(), [], -1) 
        for task, args in self.tasks.items():
            getattr(flowpfile, task)(*args) 
