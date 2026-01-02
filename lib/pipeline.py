import json

from .chat_request import ChatRequest
from .request import chat_completions
from .extractor import Extractor

class Pipeline:
    """A class holds operations and targets"""
    targets: list[str]
    prompts: list[str]
    sys_prompts: list[str]
    results: list
    action: str
    error_count: int
    newline: str|None

    def __init__(self):
        self.targets = []
        self.prompts = []
        self.sys_prompts = []
        self.results = []
        self.action = "overwrite"
        self.error_count = 0
        self.state = None
        self.newline = ""
        # TODO: add option to controll newline
        
    @classmethod
    def fromAction(cls, action):
        p = cls()
        if "target" in action:
            p.targets.append(action["target"])
        if "prompt" in action:
            p.prompts.append(action["prompt"])
        if "action" in action:
            p.action = action["action"]
        return p

    def add_result(self, result):
        self.results.append(result)

    def setStateController(self, state):
        self.state = state
        
    def execute_action(self, target, resp):
        extractor = Extractor()
        items = extractor.parse(resp)
        result = {
            "target": target,
            "outputs": items,
            "response": extractor.get_contents(resp),
            "reasoning": extractor.get_reasoning_contents(resp),
            "succeeded": False,
        }
        if self.action == "overwrite":
            if len(items) == 1:
                with open(target, "wt", encoding="utf8", newline=self.newline) as fp:
                    fp.write(items[0])
                result["succeeded"] = True
            else:
                if len(items):
                    print(f"outputs for {target} is not found, skip saving...")
                else:
                    print(f"multiple outputs for {target} are found, skip saving...")
                self.error_count += 1
            self.add_result(result)
                
        else: # print
            index = 0
            for item in items:
                print(f"---- result #{index}: ----\n")
                print(item)
                index += 1

    def get_targets(self) -> list[str]:
        return self.targets
    
    def start(self):
        req = ChatRequest()
        for prompt in self.prompts:
            req.add_user_message(prompt)

        for target in self.targets:
            with open(target, encoding="utf8") as fp:
                req.add_user_message(fp.read())
                resp = chat_completions(req.as_json())
                self.execute_action(target, resp)
