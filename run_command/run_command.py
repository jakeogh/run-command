#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement


import os
import subprocess
import sys
from pathlib import Path
from typing import Generator
from typing import List
from typing import Sequence

import click
from kcl.assertops import maxone
from kcl.configops import click_read_config
from kcl.configops import click_write_config_entry
from kcl.userops import not_root
from retry_on_exception import retry_on_exception


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
except ImportError:
    ic = eprint


# https://docs.python.org/3/library/subprocess.html#subprocess.run
def run_command(command,
                verbose: bool = False,
                debug: bool = False,
                shell: bool = True,
                expected_exit_status: int = 0,
                ignore_exit_code: bool = False,
                stdin=None,
                stderr=subprocess.STDOUT,
                popen: bool = False,
                system: bool = False,
                interactive: bool = False,
                str_output: bool = False):

    maxone([popen, interactive, system], msg='--popen --interactive and --system are mutually exclusive')

    if isinstance(command, str):
        command = os.fsencode(command)  # hm.
    if isinstance(command, list):
        try:
            command = b' '.join(command)
        except TypeError:
            command = ' '.join(command)
            command = command.encode('utf8')

    output = None
    if verbose:
        ic(command, shell)
    if popen:
        if isinstance(command, bytes):
            command = command.decode('utf8')
        #popen_instance = os.popen(command, stderr=stderr)
        popen_instance = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=stderr, stdin=stdin, shell=shell)
        if debug:
            ic(popen_instance)
        #output = popen_instance.read()
        output, errors = popen_instance.communicate()
        if verbose:
            ic(output, errors)
        exit_code = popen_instance.returncode
        if exit_code != expected_exit_status:
            #ic(command)
            ic('exit code:', exit_code, output)
            if not ignore_exit_code:
                raise subprocess.CalledProcessError(cmd=command, returncode=exit_code)
    elif system:
        if isinstance(command, bytes):
            command = command.decode('utf8')
        os.system(command)

    else:
        try:
            #check = True
            #if ignore_exit_code:
            #    check = False
            output = subprocess.check_output(command, stderr=stderr, stdin=stdin, shell=shell)
            if verbose:
                if output:
                    ic(output)
        except subprocess.CalledProcessError as error:
            if error.returncode != expected_exit_status:
                #ic(command, ignore_exit_code)
                #if verbose:
                ic(error.returncode, error.output)
                if not ignore_exit_code:
                    raise error
                output = error.output

    if str_output and output:
        output = output.decode('utf8')

    return output


@click.command()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--simulate', is_flag=True)
@click.option('--ipython', is_flag=True)
@click.option('--count', is_flag=True)
@click.option('--skip', type=int, default=False)
@click.option('--head', type=int, default=False)
@click.option('--tail', type=int, default=False)
@click.option("--printn", is_flag=True)
@click.pass_context
def cli(ctx,
        verbose: bool,
        debug: bool,
        simulate: bool,
        ipython: bool,
        count: bool,
        skip: int,
        head: int,
        tail: int,
        printn: bool,):

    null = not printn
    end = '\n'
    if null:
        end = '\x00'
    if sys.stdout.isatty():
        end = '\n'
        assert not ipython

    if (verbose or debug):
        progress = False

    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    ctx.obj['end'] = end
    ctx.obj['null'] = null
    ctx.obj['progress'] = progress
    ctx.obj['count'] = count
    ctx.obj['skip'] = skip
    ctx.obj['head'] = head
    ctx.obj['tail'] = tail
