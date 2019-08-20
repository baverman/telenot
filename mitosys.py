import os
import sys

from subprocess import run as subprocess_run
from inspect import getsource
from textwrap import dedent
from itertools import count

name_counter = count()
SHELL = ['/bin/sh', '-e', '-o', 'pipefail', '-c']


def _shell(*args, **kwargs):
    if kwargs.get('shell') != False:
        args = [SHELL + [' '.join(args)]]

    kwargs.setdefault('check', True)
    kwargs['shell'] = False
    return subprocess_run(*args, **kwargs)


def shell(*args, **kwargs):
    p = _shell(*args, **kwargs)
    return p.returncode


def shellc(*args, **kwargs):
    kwargs.setdefault('capture_output', True)
    p = _shell(*args, **kwargs)
    return p.stdout


def unarchive(data, dest):
    d, p = os.path.split(dest)
    shell(f'tar -xz --one-top-level="{p}" -C "{d}"', input=data)


def _put(src, dest, data, mode=None):
    print('Uploading', src, 'to', dest)
    with open(dest, 'wb') as f:
        f.write(data)
    if mode:
        os.chmod(dest, mode)


def symlink(target, link_name):
    tmp_name = link_name + '.tmp'
    os.symlink(target, tmp_name)
    os.rename(tmp_name, link_name)


def put(src, remote, dest, mode=None):
    data = open(src, 'rb').read()
    remote.call(_put, src, dest, data, mode)


def write_data(data, dest, mode=None):
    om = 'w' if type(data) is type(u'') else 'wb'
    with open(dest, om) as f:
        f.write(data)
    if mode:
        os.chmod(dest, mode)


class Remote:
    def __init__(self, ctx):
        self.ctx = ctx

    def shell(self, *args, **kwargs):
        return self.ctx.call(shell, *args, **kwargs)

    def shellc(self, *args, **kwargs):
        return self.ctx.call(shellc, *args, **kwargs)

    def call(self, *args, **kwargs):
        self.ctx.call(*args, **kwargs)

    def run(self, fn):
        global_name = 'tmp_fn_{}_{}'.format(fn.__name__, next(name_counter))
        def stub():
            pass
        stub.__name__ = global_name

        # print(fn.__code__, dir(fn.__code__))
        # for k in dir(fn.__code__):
        #     if not k.startswith('__'):
        #         print(k, getattr(fn.__code__, k))

        source = dedent(getsource(fn))
        fsource = ['def _closure({}):'.format(
            ', '.join(fn.__code__.co_freevars))]
        for it in source.splitlines()[1:]:
            fsource.append('   ' + it)
        fsource.append('   return {}'.format(fn.__name__))
        fsource = '\n'.join(fsource)

        freevars = dict(zip(fn.__code__.co_freevars,
                            [it.cell_contents for it in fn.__closure__ or []]))
        self.ctx.call(compile_fn, fsource, global_name, freevars, fn.__module__)
        self.ctx.call(stub)


def compile_fn(fn, gname, freevars, module):
    local_ctx = {}
    __import__(module)
    globs = vars(sys.modules[module])
    exec(fn, globs, local_ctx)
    globals()[gname] = local_ctx['_closure'](**freevars)
