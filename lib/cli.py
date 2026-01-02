import tomllib
import json
import logging

from .arg_parser import parse_arg, pre_parse_arg
from .config import Config
from .scm import SourceCodeManager
from .state import State
from .pipeline import Pipeline
from lib import pipeline

def parse_action_file(fp):
    return tomllib.load(fp)

def start():
    # pre parse to check vital options
    args = pre_parse_arg()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    config = Config()
    config.use(SourceCodeManager())
    state = State(config)
    state.transition(State.States.STARTUP)
    
    args = parse_arg()
    action = parse_action_file(args.filename)
    args.filename.close()

    p = Pipeline.fromAction(action)
    p.setStateController(state)

    state.transition(State.States.BEFORE_PROCESS, p)
    state.transition(State.States.BEFORE_ACTION, action)
    p.start()
    state.transition(State.States.AFTER_ACTION, action)
    state.transition(State.States.AFTER_PROCESS, p)

    # save logs
    with open("ot_log.json", "wt", encoding="utf8") as fp:
        json.dump(p.results, fp, ensure_ascii=False, indent=2)
