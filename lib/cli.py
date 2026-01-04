import tomllib
import json
import logging
from pathlib import Path

from .arg_parser import parse_arg, pre_parse_arg
from .config import Config
from .scm import SourceCodeManager
from .state import State
from .pipeline import Pipeline
from lib import pipeline
from .action import Action

class LogJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Path):
            return str(o)
        return super().default(o)


def start():
    # pre parse to check vital options
    args = pre_parse_arg()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config = Config()
    config.load()
    config.use(SourceCodeManager())
    state = State(config)
    state.transition(State.States.STARTUP)
    
    args = parse_arg()
    action = Action(tomllib.load(args.filename))
    args.filename.close()

    #p = Pipeline.fromAction(action)
    p = Pipeline(config, state)
    p.add_action(action)

    state.transition(State.States.BEFORE_PROCESS, p)
    p.start()
    state.transition(State.States.AFTER_PROCESS, p)

    # save logs
    with open("ot_log.json", "wt", encoding="utf8") as fp:
        json.dump(p.results, fp, ensure_ascii=False, indent=2, cls=LogJSONEncoder)
