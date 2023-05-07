# diagnostics-tk

A small and simple framework to organize and run diagnostics tests using a
simple flexible output system.

## Installation

From the root of the repo:

```
python -m pip install .
```

Directly from github:

```
python -m pip install git+https://github.com/smetj/diagnostics-tk.git
```
## Run tests

### Install test dependencies
```
python -m pip install .[test]
```

### Execute tests
```
pytest tests/
```

### Pre-commit
Support for [pre-commit](https://pre-commit.com/) is included and required to
use prior to contributing.

## Example usage

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from diagnostics_tk import DiagnosticsRunner
from diagnostics_tk.output import ConsoleTable
from diagnostics_tk.tools import exec_cli


class PublicEndpoint:
    def __init__(self, hostname, dns):
        self.hostname = hostname
        self.dns = dns

    def test_hostname_dns(self):
        """
        Can `{hostname}` be resolved using
        dns server `{dns}`?
        """
        result, reason = exec_cli(
            f"dig {self.hostname} @{self.dns}",
            stdout_pattern="status: NOERROR",
            timeout=5,
        )
        assert result, reason

    def test_host_up(self):
        """
        Is `{hostname}` reachable?
        """
        result, reason = exec_cli(
            f"nmap -sP {self.hostname}",
            exit_code=0,
            stdout_pattern="Host is up",
        )
        assert result, reason


def main():
    with DiagnosticsRunner(name="my_infra", workers=5) as runner:
        runner.register(
            "smetj.net",
            PublicEndpoint(
                hostname="smetj.net",
                dns="1.1.1.1",
            ),
        )

        runner.register("table", ConsoleTable(title="My Infra"))


if __name__ == "__main__":
    main()
```

### Output

```
2023-04-29 10:38:00,430 - DEBUG - Registered `smetj.net` as a test collection.
2023-04-29 10:38:00,430 - DEBUG - Registered `table` as an output.
2023-04-29 10:38:00,543 - INFO - my_infra::PublicEndpoint(smetj.net)::test_host_up - OK
2023-04-29 10:38:00,598 - INFO - my_infra::PublicEndpoint(smetj.net)::test_hostname_dns - OK
                                                                My Infra
+--------------------------------------------------------------------------------------------------------------------------------------+
| Name                                                   | Description                                               | Result | Reason |
|--------------------------------------------------------+-----------------------------------------------------------+--------+--------|
| my_infra::PublicEndpoint(smetj.net)::test_host_up      |  Is `smetj.net` reachable?                                | True   | n/a    |
|--------------------------------------------------------+-----------------------------------------------------------+--------+--------|
| my_infra::PublicEndpoint(smetj.net)::test_hostname_dns |  Can `smetj.net` be resolved using dns server `1.1.1.1`?  | True   | n/a    |
+--------------------------------------------------------------------------------------------------------------------------------------+
```
