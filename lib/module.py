"""module.py - module base class for O't"""

class Module:
    """A base class for modules"""

    def __init__(self):
        pass

    def loaded(self, config):
        """A callback function that is called when the module is loaded"""
        pass

    def startup(self, config):
        """A callback function that is called in CLI's startup process"""
        pass

    def before_process(self, config, pipeline):
        """A callback function that is called before pipeline process"""
        pass

    def before_action(self, config, action):
        """A callback function that is called before executing actions"""
        pass

    def after_process(self, config, pipeline):
        """A callback function that is called after pipeline process"""
        pass

    def after_action(self, config, action):
        """A callback function that is called after executing actions"""
        pass

    def cleanup(self, config):
        """A callback function that is called in CLI's cleanup process"""
        pass

