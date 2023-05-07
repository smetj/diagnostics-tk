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


import concurrent.futures
import logging
import re
import sys
from typing import Any, Callable, Dict, Type, Union

from .output import Output


class DiagnosticsRunner:
    """
    A context manager to execute registered diagnostics class methods in a
    pool of threads.

    Args:
        - name: The name to assign to the instance. This is used in logging
          output.
        - workers: The number of threads to assign to the threadpool.
    """

    def __init__(self, name: str, workers: int):
        self.name = name
        self.workers = workers

        self.diag_tests = {}
        self.outputs = []
        self.methods = []
        self.logger = self.__get_logger()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.run()
        for output in self.outputs:
            output.flush()

    def __get_logger(self) -> logging.Logger:
        """
        Creates and returns a `logger` instance.

        Returns:
            - The logger obj instance.
        """
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        root.addHandler(handler)
        return root

    def __is_diag_instance(self, obj: Any) -> bool:
        """
        Validates whether `obj` has any methods which start with `test_` which
        we then consider as a collection of tests.

        Args:
            - obj: An object instance

        Returns:
            - The conclusion
        """

        for func in dir(obj):
            if func.startswith("test_") and callable(getattr(obj, func)):
                return True
        return False

    def __render_doc_string(
        self, func: Callable, kwargs: Dict[str, Any]
    ) -> Union[str, None]:
        """
        Extracts the docstring from the provided `func` and renders it using
        the provided `kwargs`.
        """

        if func.__doc__ is None:
            self.logger.error(
                f"Failed to render docstring of function `{func.__name__}`. Reason: No docstring"
            )
        else:
            try:
                doc = func.__doc__.format(**kwargs)
                return re.sub(r"\s+", " ", doc)
            except Exception as err:
                self.logger.error(
                    f"Failed to render docstring of function `{func.__name__}`. Reason: {err}"
                )

        return None

    def __extract_test_methods(self, obj: Type):
        """
        Extracts `test_` methods from `obj` and yields all entries.

        Args:
            - obj: The class instance to extract methods from

        Yields:
            - Name of the method
            - Method object
            - Docstring

        """
        class_name = type(obj).__name__
        for name in dir(obj):
            func = getattr(obj, name)
            if name.startswith("test_") and callable(func):
                doc = self.__render_doc_string(func=func, kwargs=dict(obj.__dict__))
                yield f"{self.name}::{class_name}({obj._name})::{name}", func, doc

    def __callback(self, future: concurrent.futures.Future):
        """
        Executed as a callback for every future instance which finishes.
        This method evaluates whether the diagnostic test has raised an
        `AssertionError`. Besides this this callback runs the results of each executed
        diagnostics test through all registered output modules.

        Args:
            future: The future instance of the executed diagnostic method.
        """
        try:
            future.result()
        except AssertionError as err:
            self.logger.error(f'{future.method["name"]} - Failed. Reason: {err}')  # type: ignore
            result = False
            reason = str(err)

        else:
            self.logger.info(f'{future.method["name"]} - OK')  # type: ignore
            result = True
            reason = "n/a"

        for output in self.outputs:
            output.submit(
                future.method["name"],  # type: ignore
                future.method["doc"],  # type: ignore
                result,
                reason,
            )

    def register(self, name: str, obj: Type) -> None:
        """
        Registers `obj` as either an output or test collection.

        Args:
            - name: The name of the object.
            - obj: The obj instance
        """
        obj._name = name
        if isinstance(obj, Output):
            self.logger.debug(f"Registered `{name}` as an output.")
            self.outputs.append(obj)
        elif self.__is_diag_instance(obj):
            self.logger.debug(f"Registered `{name}` as a test collection.")
            for method_name, method, doc in self.__extract_test_methods(obj):
                self.methods.append({"name": method_name, "method": method, "doc": doc})

    def run(self):
        """
        Executes each method into a thread.
        """
        futures = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:
            for method in self.methods:
                future = executor.submit(method["method"])
                # lets piggy back and go along for the ride
                future.method = method
                future.add_done_callback(self.__callback)
                futures.append(future)

            concurrent.futures.as_completed(futures)
