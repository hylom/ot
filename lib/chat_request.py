import json

class ChatRequest:
    """ A class to build and generate request
    for OpenAI's `/v1/chat/completions API`"""
    messages: list[dict[str, str]]

    def __init__(self):
        self.messages = []

    def add_user_message(self, message: str):
        msg = { "role": "user", "content": message }
        self.messages.append(msg)

    def as_json(self):
        return json.dumps(self.serialize())

    def serialize(self):
        return { "messages": self.messages, }
