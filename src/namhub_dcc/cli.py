"""Entry point for the ``namhub-dcc`` command-line tool."""

import argparse
import logging

from namhub_dcc import __version__
from namhub_dcc.commands import COMMAND_MODULES

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="namhub-dcc",
        description="Scripts to automate steps in NAMHub data coordination.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    for module in COMMAND_MODULES:
        module.add_parser(subparsers)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
