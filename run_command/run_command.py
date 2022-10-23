#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=fixme                           # [W0511] todo is encouraged
# pylint: disable=line-too-long                   # [C0301]
# pylint: disable=too-many-instance-attributes    # [R0902]
# pylint: disable=too-many-lines                  # [C0302] too many lines in module
# pylint: disable=invalid-name                    # [C0103] single letter var names, name too descriptive
# pylint: disable=too-many-return-statements      # [R0911]
# pylint: disable=too-many-branches               # [R0912]
# pylint: disable=too-many-statements             # [R0915]
# pylint: disable=too-many-arguments              # [R0913]
# pylint: disable=too-many-nested-blocks          # [R1702]
# pylint: disable=too-many-locals                 # [R0914]
# pylint: disable=too-few-public-methods          # [R0903]
# pylint: disable=no-member                       # [E1101] no member for base
# pylint: disable=attribute-defined-outside-init  # [W0201]
# pylint: disable=too-many-boolean-expressions    # [R0916] in if statement
from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Sequence
from math import inf
from pathlib import Path
from typing import Generator

import click
# from asserttool import ic
from asserttool import maxone
from clicktool import click_add_options
from clicktool import click_global_options
from epprint import epprint
from eprint import eprint

# from retry_on_exception import retry_on_exception


def ask_command(command):
    eprint("Press ENTER to execute command:")
    epprint(command)
    result = input()
    if result:
        sys.exit(1)


# https://docs.python.org/3/library/subprocess.html#subprocess.run
def run_command(
    command,
    verbose: bool | int | float,
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
        epprint(command, shell)
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
        if verbose == inf:
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
                command, stderr=stderr, stdin=stdin, shell=shell
            )
            if verbose:
                if output:
                    epprint(output)
                    sys.stderr.buffer.write(output)
        except subprocess.CalledProcessError as error:
            if error.returncode != expected_exit_status:
                # ic(command, ignore_exit_code)
                # if verbose:
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
    verbose: bool | int | float,
    verbose_inf: bool,
):
    pass
