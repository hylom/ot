"""state.py - state controller for O't."""

from enum import Enum
import logging
logger = logging.getLogger(__name__)

class State:
    """A class to retain state and controll state transition"""
    class States(Enum):
        UNDEFINED = 0
        STARTUP = 1
        BEFORE_PROCESS = 2
        BEFORE_ACTION = 3
        AFTER_ACTION = 4
        AFTER_PROCESS = 5
        CLEANUP = 10

    current_state: States
    
    def __init__(self, config):
        self.current_state = self.States.UNDEFINED
        self.config = config

    def _get_handler(self, state: States):
        if state == self.States.STARTUP:
            return lambda x, cfg, param: x.startup(cfg)
        if state == self.States.BEFORE_PROCESS:
            return lambda x, cfg, param: x.before_process(cfg, param)
        if state == self.States.BEFORE_ACTION:
            return lambda x, cfg, param: x.before_action(cfg, param)
        if state == self.States.AFTER_ACTION:
            return lambda x, cfg, param: x.after_action(cfg, param)
        if state == self.States.AFTER_PROCESS:
            return lambda x, cfg, param: x.after_process(cfg, param)
        if state == self.States.CLEANUP:
            return lambda x, cfg, param: x.cleanup(cfg)
        return lambda x, cfg, param: False

    def transition(self, state: States, param=None):
        self.current_state = state
        handler = self._get_handler(state)
        
        for m in self.config.get_modules():
            logger.debug(f"execute {m} handler for {state}")
            handler(m, self.config, param)

        logger.debug(f"all {state} handlers are finished")
