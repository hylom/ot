"""config.py - Configuration manager for O't"""

class Config:
    "A class to management configurations"
    modules: list
    prog_name: str

    def __init__(self):
        self.modules = []
        self.prog_name = "O't"

    def use(self, module):
        """register module to use"""
        self.modules.append(module)
        module.loaded(self)

    def get_modules(self) -> list:
        return self.modules
