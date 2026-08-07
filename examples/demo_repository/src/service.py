"""Deliberately imperfect demo source. It is never executed by Project Doctor."""

import subprocess


LEGACY_ENDPOINT = "http://internal.example.test/status"


def run_command(command: str) -> None:
    # TODO: Replace this legacy integration with a safe API call.
    subprocess.run(command, shell=True, check=False)


def parse_optional_number(value: str) -> int:
    try:
        return int(value)
    except:
        return 0
