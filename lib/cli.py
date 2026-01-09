import sys
import tomllib
import json
import logging
from pathlib import Path
import argparse
from datetime import datetime

from .arg_parser import parse_arg
from .config import Config
from .scm import SourceCodeManager
from .state import State
from .pipeline import Pipeline
from lib import pipeline
from .action import Actions
from .chat_request import ChatRequest

class LogJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Path):
            return str(o)
        if isinstance(o, ChatRequest):
            return o.serialize()
        return super().default(o)

def is_debug_enabled() -> bool:
    return any([(x == "--debug") for x in sys.argv[1:]])

def get_json_log_pathname(prefix: str="ot-log") -> str:
    dt = datetime.now()
    return f"{prefix}-{dt.strftime("%Y%m%d-%H%M%S")}.json"

def start():
    # check if debug option is given
    if is_debug_enabled():
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config = Config()
    config.load()
    config.use(SourceCodeManager())
    state = State(config)
    state.transition(State.States.STARTUP)
    
    args = parse_arg()
    action = None
    if args.command == "run":
        action = Actions.create_action(tomllib.load(args.filename))
        args.filename.close()
    else:
        action = Actions.create_from_arguments(args)

    if action is None:
        print(sys.stderr, "Nothing to do.\n")
        return

    p = Pipeline(config, state)
    p.add_action(action)

    state.transition(State.States.BEFORE_PROCESS, p)
    p.start()
    state.transition(State.States.AFTER_PROCESS, p)

    # save logs
    pathname = get_json_log_pathname()
    with open(pathname, "wt", encoding="utf8") as fp:
        json.dump(p.results, fp, ensure_ascii=False, indent=2, cls=LogJSONEncoder)
