#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_style.py
#

from pathlib import Path
from subprocess import run

import black


def test_ruff_conformance():
    """
    Test code passed flake8
    """
    ignore = [
        "E501",  # E501 line too long (163 > 79 characters)
    ]
    result = run(
        ["ruff", "--ignore", ",".join(ignore), "diagnostics_tk/"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        assert False, result.stdout.decode()


def test_black():
    """
    Test whether code is formatted with black
    """

    for path in Path("diagnostics_tk").rglob("*.py"):
        assert not black.format_file_in_place(
            Path(path),
            fast=False,
            mode=black.FileMode(),
        )
