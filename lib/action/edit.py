"""Implements `edit` action"""

import time
import logging
logger = logging.getLogger(__name__)

from .action import Action

class EditAction(Action):
    """A class implements `edit` action"""
    action_name = "edit"

    def __init__(self, action=None):
        super().__init__(action)

    def execute_per_target(self, target, pipeline):
        # prepare and send request
        req = self.create_request()

        content = pipeline.load_text_file(target)
        req.add_user_message(content)

        start_sec = time.monotonic()
        logger.info(f'start completions for "{str(target)}"...')
        resp = pipeline.execute_chat_completions(req.as_json())
        elapsed = time.monotonic() - start_sec;
        logger.info(f'completions for "{str(target)}" done. Eelapsed: {elapsed} sec.')

        # Process result
        extractor = self.get_extractor(self.action)
        items = extractor.parse(resp)
        result = {
            "target": target,
            "outputs": items,
            "response": extractor.get_contents(resp),
            "reasoning": extractor.get_reasoning_contents(resp),
            "succeeded": False,
            "elapsed_time": elapsed,
        }
        
        if len(items) == 1:
            pipeline.save_text_file(target, items[0])
            result["succeeded"] = True
        else:
            pipeline.error_count += 1
            if len(items) == 0:
                logger.error(f"outputs for {target} is not found, skip saving...")
            else:
                logger.error(f"multiple outputs for {target} are found, skip saving...")
        pipeline.add_result(result)

    def execute(self, pipeline):
        for target in self.get_targets():
            self.execute_per_target(target, pipeline)

Action.add_action(EditAction)
