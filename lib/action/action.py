"""Impelements Action"""

from collections.abc import Callable
import argparse
from pathlib import Path
import re
import logging
logger = logging.getLogger(__name__)

from ..chat_request import ChatRequest
from ..extractor import Extractor
from ..arg_parser import add_subcommand

COMMON_PARAMETERS = {
    "prompt": {
        "type": (str, list),
        "description": "user prompt",
        "short_name": "p"
    },
    "sys_prompt": {
        "type": (str, list),
        "description": "system prompt",
        "short_name": "s"
    },
    "target": {
        "type": (str, list),
        "description": "files to process",
        "short_name": "t"
    },
    "output": {
        "type": str,
        "description": "output file",
        "short_name": "o"
    },
}

class TargetParser:
    """A parser for targets"""
    def __init__(self):
        pass

    def _is_wildcards(self, target: str) -> bool:
        if "*" in target:
            return True
        if "?" in target:
            return True
        if re.search(r"\[(.+)]", target) is not None:
            return True
        return False

    def parse(self, targets: list[str]) -> list[Path]:
        """parse and glob given relative filenames"""
        results: list[Path] = []
        for target in targets:
            if self._is_wildcards(target):
                results.extend(list(Path(".").glob(target)))
            else:
                results.append(Path(target))
        return results

class ActionError(Exception):
    """An error class that represent action related error"""
    def __init__(self, message):
        super().__init__(message)

class Actions:
    """A class to manage actions"""
    actions: dict[str, type] = {}
    
    @classmethod
    def add_action(cls, actionClass: type):
        """add Action subclass"""
        if actionClass.name:
            cls.actions[actionClass.name] = actionClass
            if not actionClass.description:
                logger.warning(f"description is not given for Action {actionClass}.")
            p = add_subcommand(actionClass.name, actionClass.description)
            actionClass.add_subcommand(p)

    @classmethod
    def create_action(cls, action: dict):
        """create instance of Action subclass from dict"""
        action_name = action.get("action", "")
        if len(action_name) == 0:
            raise ActionError("no action is given")
        action_cls = cls.actions.get(action_name, None)
        if action_cls is None:
            raise ActionError(f"no action is registered for {action_name}")
        return action_cls(action)

    @classmethod
    def create_from_arguments(cls, args):
        action_name = args.command
        action_cls = cls.actions.get(action_name, None)
        if action_cls is None:
            raise ActionError(f"no action is registered for {action_name}")
        return action_cls(vars(args))

# decorator for Action derivative classes
def parameter(name: str, types: type|tuple[type, ...],
              short_name: str|None=None) -> Callable[[type], type]:
    """register parameter"""
    return lambda cls: cls.add_parameter(name, types, short_name)

def add_common_parameter(cls, name: str|tuple[str]) -> type:
    if not name in COMMON_PARAMETERS:
        logger.warning(f"{name} is not in prepared parameters")
        return cls
    p = COMMON_PARAMETERS[name]
    cls.add_parameter(name, p["type"], p["description"], p["short_name"])
    return cls

def common_parameter(name: str) -> Callable[[type], type]:
    """register common parameter"""
    return lambda cls: add_common_parameter(cls, name)

class Action:
    """A class represents action"""
    name: str = ""
    description: str = ""
    parameter: dict[str, type|tuple[type, ...]] = {}
    parameter_short_name: dict[str, str] = {}
    parameter_description: dict[str, str] = {}

    targets: list[str]
    prompts: list[str]
    sys_prompts: list[str]
    output: str

    @classmethod
    def add_subcommand(cls, parser):
        for pname in cls.parameter:
            args: list[str] = []
            xargs: dict[str, str] = {}
            short = cls.parameter_short_name.get(pname)
            if short:
                args.append(f"-{short}")
            args.append(f"--{pname.replace("_", "-")}")
            descr = cls.parameter_description.get(pname)
            if descr:
                xargs["help"] = descr
            parser.add_argument(*args, **xargs)

    @classmethod
    def add_parameter(cls, name: str,
                      types: type|tuple[type, ...],
                      param_description: str|None=None,
                      short_name: str|None=None) -> type:
        cls.parameter[name] = types
        if short_name is not None:
            cls.parameter_short_name[name] = short_name
        if param_description is not None:
            cls.parameter_description[name] = param_description
        return cls

    def __init__(self, action=None):
        self.targets = []
        self.prompts = []
        self.sys_prompts = []
        self.output = ""
        if action is not None:
            self.set_action(action)
    
    def set_action(self, action):
        if "target" in action:
            if isinstance(action["target"], list):
                self.targets.extend(action["target"])
            else:
                self.targets.append(action["target"])
        if "prompt" in action:
            self.prompts.append(action["prompt"])

    def get_targets(self) -> list[Path]:
        return TargetParser().parse(self.targets)

    def get_targets_to_commit(self) -> list[Path]:
        return TargetParser().parse(self.targets)

    def create_request(self) -> ChatRequest:
        """create and prepare ChatRequest object"""
        req = ChatRequest()
        for prompt in self.prompts:
            req.add_user_message(prompt)
        return req

    def get_extractor(self, action: str):
        return Extractor()

# add "run" subcommand
run = add_subcommand("run", "run defined actions")
run.add_argument("filename", type=argparse.FileType("rb"),
                 help="action file (TOML format) to run")
