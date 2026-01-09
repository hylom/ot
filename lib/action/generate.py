"""Implements `generate` action"""

import time
import logging
from pathlib import Path
logger = logging.getLogger(__name__)

from .action import Action, Actions, common_parameter

@common_parameter("prompt")
@common_parameter("sys_prompt")
@common_parameter("output")
class GenerateAction(Action):
    """A class implements `generate` action"""
    name = "generate"
    description = "generate file(s)"

    def __init__(self, action=None):
        super().__init__(action)

    def execute(self, pipeline):
        # prepare and send request
        req = self.create_request()

        count = 0
        for target in self.get_targets():
            content = pipeline.load_text_file(target)
            req.add_user_message(f"{target}:")
            req.add_user_message(content)
            count += 1

        start_sec = time.monotonic()
        logger.info(f'start completions for {count} files...')
        resp = pipeline.execute_chat_completions(req.as_json())
        elapsed = time.monotonic() - start_sec;
        logger.info(f'completions done. Eelapsed: {elapsed} sec.')

        # Process result
        extractor = self.get_extractor(self.name)
        items = extractor.get_contents(resp)
        result = {
            "target": self.get_targets(),
            "outputs": items,
            "response": extractor.get_contents(resp),
            "reasoning": extractor.get_reasoning_contents(resp),
            "succeeded": False,
            "elapsed_time": elapsed,
        }
        index = 0
        for item in items:
            print(f"---- result #{index}: ----\n")
            print(item)
            index += 1
        pipeline.add_result(result)

    def get_targets_to_commit(self) -> list[Path]:
        return []

Actions.add_action(GenerateAction)
