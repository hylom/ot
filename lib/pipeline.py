"""Implements Pipeline"""

import json

from .chat_request import ChatRequest
from .request import chat_completions
from .state import State
from urllib.error import URLError
import logging
logger = logging.getLogger(__name__)

class Pipeline:
    """A class holds operations and targets"""
    results: list
    error_count: int
    output_newline: str|None
    input_encoding: str
    output_encoding: str
    state: State

    def __init__(self, config, state: State):
        self.results = []
        self.error_count = 0
        self.state = state
        self.config = config
        self.output_newline = config.get("output", {}).get("newline", None)
        self.output_encoding = config.get("output", {}).get("encoding", "utf8")
        self.input_encoding = config.get("input", {}).get("encoding", "utf8")
        self.actions = []
        
    def add_action(self, action):
        self.actions.append(action)

    def add_result(self, result):
        self.results.append(result)

    def start(self):
        for action in self.actions:
            self.state.transition(State.States.BEFORE_ACTION, action)
            try:
                action.execute(self)
            except URLError as e:
                logger.error(f"failed to connect to server: {e}")
                continue
            self.state.transition(State.States.AFTER_ACTION, action)

    def load_text_file(self, filename: str) -> str:
        with open(filename, "rt", encoding=self.input_encoding) as fp:
            result = fp.read()
        return result

    def save_text_file(self, filename: str, content: str):
        with open(filename, "wt",
                  encoding=self.output_encoding,
                  newline=self.output_newline) as fp:
            fp.write(content)
        
    def execute_chat_completions(self, request: str):
        resp = chat_completions(request, self.config)
        return resp
