#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK


import argcomplete
import argparse
import sys
from cli import Cli


cli = Cli()
# argparser and argcompletion
parser = argparse.ArgumentParser()
parser.add_argument(
    "command",
    help="Command to call.",
    type=str,
    choices=cli.getCommands()
)
parser.add_argument(
    "--force",
    help="skip asking for permission",
    action='store_true',
    default=False
)
parser.add_argument(
    "--dryrun",
    help="do not write to disk",
    action='store_true',
    default=False
)
argcomplete.autocomplete(parser)
arguments = parser.parse_args()

if __name__ == '__main__':
    try:
        cli.dispatch(arguments)
    except Exception as e:
        print('run-time error:', e)
        sys.exit(1)