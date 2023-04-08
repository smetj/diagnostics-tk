#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  console_table.py
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

from rich import box
from rich.console import Console
from rich.table import Table

from . import Output


class ConsoleTable(Output):
    def __init__(self, title="Diagnostic results."):
        self.table = Table(title=title, box=box.ASCII, show_lines=True)
        self.table.add_column("Name", justify="left", style="cyan", no_wrap=True)
        self.table.add_column("Description", style="magenta")
        self.table.add_column("Result", justify="left", style="green")
        self.table.add_column("Reason", justify="left", style="green")

    def submit(self, name, description, result, reason):
        self.table.add_row(name, description, str(result), reason)

    def flush(self):
        console = Console()
        console.print(self.table)
