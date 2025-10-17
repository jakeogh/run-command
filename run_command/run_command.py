#!/usr/bin/env python3
# -*- coding: utf8 -*-

from __future__ import annotations

import os
import subprocess
import sys

import click
from asserttool import maxone
from clicktool import click_add_options
from clicktool import click_global_options
from epprint import epprint
from eprint import eprint


def ask_command(command):
    eprint("Press ENTER to execute command:")
    epprint(command)
    result = input()
    if result:
        sys.exit(1)


# https://docs.python.org/3/library/subprocess.html#subprocess.run
def run_command(
    command,
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
    verbose: bool = False,
):

    maxone(
        [popen, interactive, system],
        msg="--popen --interactive and --system are mutually exclusive",
    )
    maxone(
        [system, expected_exit_status],
        msg="os.system() can not check the exit status of a command",
    )

    if isinstance(command, str):
        command = os.fsencode(command)  # hm.
    if isinstance(command, list):
        try:
            command = b" ".join(command)
        except TypeError:
            command = " ".join(command)
            command = command.encode("utf8")

    output = None
    if verbose:
        epprint(
            f"\n{command=}",
            f"{shell=}",
            f"{system=}",
            f"{popen=}\n",
        )
    if popen:
        if isinstance(command, bytes):
            command = command.decode("utf8")
        # popen_instance = os.popen(command, stderr=stderr)
        if ask:
            ask_command(command)
        popen_instance = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=stderr,
            stdin=stdin,
            shell=shell,
        )
        if verbose:
            epprint(popen_instance)
        # output = popen_instance.read()
        output, errors = popen_instance.communicate()
        if verbose:
            epprint(output, errors)
        exit_code = popen_instance.returncode
        if exit_code != expected_exit_status:
            # ic(command)
            epprint("exit code:", exit_code, output)
            if not ignore_exit_code:
                raise subprocess.CalledProcessError(cmd=command, returncode=exit_code)
    elif system:
        if isinstance(command, bytes):
            command = command.decode("utf8")
        if ask:
            ask_command(command)
        os.system(command)

    else:
        try:
            # check = True
            # if ignore_exit_code:
            #    check = False
            if ask:
                ask_command(command)
            output = subprocess.check_output(
                command,
                stderr=stderr,
                stdin=stdin,
                shell=shell,
            )
            if verbose:
                if output:
                    epprint(output)
                    # sys.stderr.buffer.write(output)
        except subprocess.CalledProcessError as error:
            if error.returncode != expected_exit_status:
                # ic(command, ignore_exit_code)
                epprint(error.returncode, error.output)
                if not ignore_exit_code:
                    raise error
                output = error.output

    if str_output and output:
        output = output.decode("utf8")

    return output


@click.command()
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    verbose_inf: bool,
    verbose: bool = False,
):
    pass
