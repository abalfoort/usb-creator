#!/usr/bin/env python3

import subprocess
import re
import threading
from os.path import expanduser
from fuzzywuzzy import fuzz

def shell_exec_popen(command, kwargs={}):
    print(('Executing:', command))
    return subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE, **kwargs)


def shell_exec(command):
    print(('Executing:', command))
    return subprocess.call(command, shell=True)


def getoutput(command):
    #return shell_exec(command).stdout.read().strip()
    try:
        output = subprocess.check_output(command, shell=True).decode('utf-8').strip().replace('\r\n', '\n').replace('\r', '\n').split('\n')
    except:
        output = []
    return output


def chroot_exec(command):
    command = command.replace('"', "'").strip()  # FIXME
    return shell_exec('chroot /target/ /bin/sh -c "%s"' % command)


def memoize(func):
    """ Caches expensive function calls.

    Use as:

        c = Cache(lambda arg: function_to_call_if_yet_uncached(arg))
        c('some_arg')  # returns evaluated result
        c('some_arg')  # returns *same* (non-evaluated) result

    or as a decorator:

        @memoize
        def some_expensive_function(args [, ...]):
            [...]

    See also: http://en.wikipedia.org/wiki/Memoization
    """
    class memodict(dict):
        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = func(*key)
            return ret
    return memodict()


def get_config_dict(file, key_value=re.compile(r'^\s*(\w+)\s*=\s*["\']?(.*?)["\']?\s*(#.*)?$')):
    """Returns POSIX config file (key=value, no sections) as dict.
    Assumptions: no multiline values, no value contains '#'. """
    d = {}
    with open(file) as f:
        for line in f:
            try:
                key, value, _ = key_value.match(line).groups()
            except AttributeError:
                continue
            d[key] = value
    return d


# Check if running in VB
def runningInVirtualBox():
    dmiBIOSVersion = getoutput("dmidecode -t0 | grep 'Version:' | awk -F ': ' '{print $2}'")
    dmiSystemProduct = getoutput("dmidecode -t1 | grep 'Product Name:' | awk -F ': ' '{print $2}'")
    dmiBoardProduct = getoutput("dmidecode -t2 | grep 'Product Name:' | awk -F ': ' '{print $2}'")
    if dmiBIOSVersion != "VirtualBox" and dmiSystemProduct != "VirtualBox" and dmiBoardProduct != "VirtualBox":
        return False
    return True


# Check if is 64-bit system
def isAmd64():
    machine = getoutput("uname -m")[0]
    if machine == "x86_64":
        return True
    return False


# Check for backports
def has_backports():
    try:
        bp = getoutput("grep backports /etc/apt/sources.list | grep -v ^#")[0]
    except:
        bp = ''
    if bp.strip() == "":
        try:
            bp = getoutput("grep backports /etc/apt/sources.list.d/*.list | grep -v ^#")[0]
        except:
            bp = ''
    if bp.strip() != "":
        return True
    return False


def getPackageVersion(package, candidate=False):
    cmd = "env LANG=C bash -c 'apt-cache policy %s | grep \"Installed:\"'" % package
    if candidate:
        cmd = "env LANG=C bash -c 'apt-cache policy %s | grep \"Candidate:\"'" % package
    lst = getoutput(cmd)[0].strip().split(' ')
    version = lst[-1]
    if 'none' in version:
        version = ''
    return version


# Convert string to number
def str_to_nr(stringnr, toInt=False):
    nr = 0
    # Might be a int or float: convert to str
    stringnr = str(stringnr).strip()
    try:
        if toInt:
            nr = int(stringnr)
        else:
            nr = float(stringnr)
    except ValueError:
        nr = 0
    return nr


def get_logged_user():
    return getoutput("logname")[0]


def get_user_home():
    return expanduser("~%s" % get_logged_user())


# Fuzzy string comparison
# fuzzy_level: 1 = no string pre-processing (differnce in character case)
#              2 = optimal partial logic
#              3 = includes string pre-processing (remove punctuation, lower case, etc)
#              4 = ptakes out the common tokens (the intersection) and then makes a pairwise comparisons
def get_fuzzy_ratio(string1, string2, fuzzy_level=1):
    if fuzzy_level == 2:
        ratio = fuzz.partial_ratio(string1,string2)
    elif fuzzy_level == 3:
        ratio = fuzz.token_sort_ratio(string1,string2)
    elif fuzzy_level == 4:
        ratio = fuzz.token_set_ratio(string1,string2)
    else:
        ratio = fuzz.ratio(string1,string2)
    return ratio


# Class to run commands in a thread and return the output in a queue
class ExecuteThreadedCommands(threading.Thread):

    def __init__(self, commandList, theQueue=None, returnOutput=False):
        super(ExecuteThreadedCommands, self).__init__()
        self.commands = commandList
        self.queue = theQueue
        self.returnOutput = returnOutput

    def run(self):
        if isinstance(self.commands, (list, tuple)):
            for cmd in self.commands:
                self.exec_cmd(cmd)
        else:
            self.exec_cmd(self.commands)

    def exec_cmd(self, cmd):
        if self.returnOutput:
            ret = getoutput(cmd)
        else:
            ret = shell_exec(cmd)
        if self.queue is not None:
            self.queue.put(ret)
