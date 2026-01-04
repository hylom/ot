"""Impelements Action"""

from pathlib import Path
import re
import time
import logging
logger = logging.getLogger(__name__)

from .chat_request import ChatRequest
from .extractor import Extractor

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

class Action:
    """A class represents action"""
    action: str
    targets: list[str]
    prompts: list[str]
    sys_prompts: list[str]
    
    def __init__(self, action=None):
        self.action = "edit"
        self.targets = []
        self.prompts = []
        self.sys_prompts = []
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
        if "action" in action:
            self.action = action["action"]

    def execute_per_target(self, target:Path, pipeline):
        # prepare and send request
        req = ChatRequest()
        for prompt in self.prompts:
            req.add_user_message(prompt)

        content = pipeline.load_text_file(target)
        req.add_user_message(content)

        start_sec = time.monotonic()
        logger.info(f'start completions for "{str(target)}"...')
        resp = pipeline.execute_chat_completions(req.as_json())
        elapsed = time.monotonic() - start_sec;
        logger.info(f'completions for "{str(target)}" done. Eelapsed: {elapsed} sec.')

        # Process result
        extractor = Extractor()
        items = extractor.parse(resp)
        result = {
            "target": target,
            "outputs": items,
            "response": extractor.get_contents(resp),
            "reasoning": extractor.get_reasoning_contents(resp),
            "succeeded": False,
            "elapsed_time": elapsed,
        }
        if self.action == "edit":
            if len(items) == 1:
                pipeline.save_text_file(target, items[0])
                result["succeeded"] = True
            else:
                if len(items):
                    logger.error(f"multiple outputs for {target} are found, skip saving...")
                else:
                    logger.error(f"outputs for {target} is not found, skip saving...")
                pipeline.error_count += 1
            pipeline.add_result(result)
                
        else: # print
            index = 0
            for item in items:
                print(f"---- result #{index}: ----\n")
                print(item)
                index += 1

    def get_targets(self) -> list[Path]:
        return TargetParser().parse(self.targets)

    def execute(self, pipeline):
        for target in self.get_targets():
            self.execute_per_target(target, pipeline)
