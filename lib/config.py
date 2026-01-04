"""config.py - Configuration manager for O't"""

import tomllib
from pathlib import Path

class Config:
    "A class to management configurations"
    modules: list
    prog_name: str
    config_file: str
    config: dict

    def __init__(self):
        self.modules = []
        self.prog_name = "O't"
        self.config_file = "ot_config.toml"
        self.config = {}

    def find_config_file(self) -> Path:
        # search current directory
        p = Path(self.config_file)
        if p.exists():
            return p
        p = Path(__file__)
        p = p.parent.parent / self.config_file
        if p.exists():
            return p
        return Path(self.config_file)

    def get(self, key: str, default=None):
        """return config value"""
        return self.config.get(key, default)

    def use(self, module):
        """register module to use"""
        self.modules.append(module)
        module.loaded(self)

    def load(self):
        """load default configuration file"""
        fn = self.find_config_file()
        with open(fn, "rb") as fp:
            cfg = tomllib.load(fp)
        self.config.update(cfg)

    def get_modules(self) -> list:
        return self.modules


