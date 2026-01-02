import re

class Extractor:
    """A class to extract contents from chat completions API response"""
    config: dict
    mode: str

    def __init__(self, config=None):
        self.config = {}
        if config is not None:
            self.config.update(config)

        # set configuration properties
        self.mode = self.config.get("mode", "markdown")

    def _parse_choice(self, choice: dict) -> list[str]:
        if "message" not in choice:
            return []
        content = choice["message"].get("content", "")
        return self._parse_content(content)

    def _parse_content(self, content: str) -> list[str]:
        if self.mode == "markdown":
            return self._parse_markdown(content)
        return []

    def _parse_markdown(self, content: str) -> list[str]:
        rex_begin_end = re.compile(r"^```")
        is_capture = False
        buf = []
        results = []
        for l in content.splitlines(keepends=True):
            if rex_begin_end.match(l):
                if is_capture:
                    is_capture = False
                    results.append("".join(buf))
                    buf = []
                else:
                    is_capture = True
                continue
            if not is_capture:
                continue
            buf.append(l)
        if len(buf):
            results.append("".join(buf))
        return results

    def parse(self, resp_dict: dict) -> list[str]:
        results = []
        for  choice in resp_dict.get("choices", []):
            items = self._parse_choice(choice)
            if len(items):
                results.extend(items)
        return results

    def get_contents(self, resp_dict: dict) -> list[str]:
        results = []
        for  choice in resp_dict.get("choices", []):
            if "message" in choice:
                content = choice["message"].get("content", "")
                results.append(content)
        return results

    def get_reasoning_contents(self, resp_dict: dict) -> list[str]:
        results = []
        for  choice in resp_dict.get("choices", []):
            if "message" in choice:
                content = choice["message"].get("reasoning_content", "")
                results.append(content)
        return results
            
