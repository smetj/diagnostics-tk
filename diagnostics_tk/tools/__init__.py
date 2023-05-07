#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
#
# The MIT License (MIT)
#
# Copyright © 2023 Jelle Smet <development@smetj.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import subprocess
from typing import Tuple


def exec_cli(
    command, exit_code=None, stdout_pattern=None, stderr_pattern=None, timeout=60
) -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            start_new_session=True,
        )
    except subprocess.TimeoutExpired:
        return False, f"Test timed out after '{timeout}' seconds."

    if exit_code is not None:
        if result.returncode != exit_code:
            return (
                False,
                f"Exit code is '{result.returncode}' instead of the expected '{exit_code}'.",
            )

    if stdout_pattern is not None:
        if not re.search(stdout_pattern, result.stdout.decode(), re.MULTILINE):
            return False, f"STDOUT did not match regex '{stdout_pattern}'."

    if stderr_pattern is not None:
        if not re.search(stderr_pattern, result.stderr.decode(), re.MULTILINE):
            return False, f"STDERR did not match regex '{stdout_pattern}'."

    return (True, "Good")
