import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="enable debug output",
                    action="store_true")
subparsers = parser.add_subparsers(dest="command", required=True,
                                   title="subcommands",
                                   help="actions to run")

def parse_arg():
    return parser.parse_args()

def add_subcommand(command: str, help:str|None=None) -> argparse.ArgumentParser:
    p = subparsers.add_parser(command, help=help)
    return p
    
