"""Impelements Action"""

from pathlib import Path
import re
import logging
logger = logging.getLogger(__name__)

from ..chat_request import ChatRequest
from ..extractor import Extractor

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

class Action:
    """A class represents action"""
    action: str
    targets: list[str]
    prompts: list[str]
    sys_prompts: list[str]
    actions: dict[str, type] = {}
    action_name = ""

    @classmethod
    def add_action(cls, actionClass: type):
        """add action subclass"""
        if actionClass.action_name:
            cls.actions[actionClass.action_name] = actionClass

    @classmethod
    def create_action(cls, action: dict):
        action_name = action.get("action", "")
        if len(action_name) == 0:
            raise ActionError("no action is given")
        action_cls = cls.actions.get(action_name, None)
        if action_cls is None:
            raise ActionError(f"no action is registered for {action_name}")
        return action_cls(action)
    
    def __init__(self, action=None):
        self.action = ""
        self.targets = []
        self.prompts = []
        self.sys_prompts = []
        if action is not None:
            self.set_action(action)
    
    def set_action(self, action):
        if "action" in action:
            self.action = action["action"]
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

