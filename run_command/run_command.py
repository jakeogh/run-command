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
from math import inf
from pathlib import Path
from typing import Generator
from typing import List
from typing import Sequence

import click
from asserttool import eprint
from asserttool import ic
from asserttool import maxone
from clicktool import click_add_options
from clicktool import click_global_options

#from retry_on_exception import retry_on_exception


def ask_command(command):
    eprint("Press ENTER to execute command:")
    ic(command)
    result = input()
    if result:
        sys.exit(1)


# https://docs.python.org/3/library/subprocess.html#subprocess.run
def run_command(command,
                verbose: int,
                shell: bool = True,
                expected_exit_status: int = None,
                ignore_exit_code: bool = False,
                stdin=None,
                stderr=subprocess.STDOUT,
                popen: bool = False,
                system: bool = False,
                interactive: bool = False,
                str_output: bool = False,
                ask: bool = False,
                ):

    maxone([popen, interactive, system], msg='--popen --interactive and --system are mutually exclusive')
    maxone([system, expected_exit_status], msg='os.system() can not check the exit status of a command')

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
        if ask:
            ask_command(command)
        popen_instance = subprocess.Popen(command,
                                          stdout=subprocess.PIPE,
                                          stderr=stderr,
                                          stdin=stdin,
                                          shell=shell,)
        if verbose == inf:
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
        if ask:
            ask_command(command)
        os.system(command)

    else:
        try:
            #check = True
            #if ignore_exit_code:
            #    check = False
            if ask:
                ask_command(command)
            output = subprocess.check_output(command, stderr=stderr, stdin=stdin, shell=shell)
            if verbose:
                if output:
                    ic(output)
                    sys.stderr.buffer.write(output)
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
@click_add_options(click_global_options)
@click.pass_context
def cli(ctx,
        verbose: int,
        verbose_inf: bool,
        ):
    pass
