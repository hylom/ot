"""scm.py - source code management module for O't."""

import subprocess
import logging
from datetime import datetime

from .module import Module
from .interact import confirm, prompt

logger = logging.getLogger(__name__)

def execute_git(subcmd: str, error_check=True) -> subprocess.CompletedProcess:
    """execute git command with given subcommand"""
    cmd = "git " + subcmd
    result = subprocess.run(cmd, text=True, capture_output=True, encoding="utf8")
    if (error_check and result.returncode != 0):
        err = result.stderr
        msg = f"git command failed: {err}"
        raise ScmError(msg)
    return result

class ScmError(Exception):
    """An error class that represent repository controll related error"""
    def __init__(self, message):
        super().__init__(message)

def get_repo_status(config):
    result = execute_git("status", error_check=False)
    
    if result.returncode != 0:
        err = result.stderr
        msg = f"You need to execute {config.prog_name} in git repository: {err}"
        raise ScmError(msg)
    return result.stdout

def get_current_branch_name(config):
    result = execute_git("branch --no-color --show-current")
    return result.stdout.strip()

def create_and_switch_branch(config, branch_name: str):
    result = execute_git(f"checkout -b {branch_name}")
    return result.stdout.strip()

def is_file_managed(config, file_path) -> bool:
    result = execute_git(f"ls-files {file_path}")
    r = result.stdout.strip()
    logger.debug(f"is_file_managed - {file_path}: {r}")
    return len(r) > 0

def is_file_changed(config, file_path) -> bool:
    result = execute_git(f"diff {file_path}")
    r = result.stdout.strip()
    logger.debug(f"is_file_changed - {file_path}: {r}")
    return len(r) > 0

def add_file(config, file_path):
    result = execute_git(f"add {file_path}")
    r = result.stdout.strip()
    logger.debug(f"add_file - {file_path}: {r}")

def commit(config, message):
    result = execute_git(f'commit -m "{message}"')
    r = result.stdout.strip()
    logger.debug(f"commit: {r}")

class SourceCodeManager(Module):
    """A module class to manage source codes"""

    def __init__(self):
        pass

    def generate_branch_name(self):
        dt = datetime.now()
        return f"ot-action-{dt.strftime("%Y-%m-%d-%H-%M")}"

    def generate_commit_message(self, pipeline):
        msg = " ".join(pipeline.prompts)
        return f"O't-mated: {msg}"
    
    def before_process(self, config, pipeline):
        """check git repository status"""
        # check repository status
        rs = get_repo_status(config)
        logger.debug(rs)

        # check branch
        branch = get_current_branch_name(config)
        logger.debug(branch)
        if branch == "master" or branch == "main":
            msg = f"Current branch is {branch}, and it is not recommend to execute {config.prog_name} in {branch} branch. Do you want to create a new branch?"
            if not confirm(msg):
                raise ScmError("inappropriate branch")
            msg = "branch name to create"
            branch_name = prompt(msg, self.generate_branch_name())
            logger.debug(branch_name)
            logger.info(create_and_switch_branch(config, branch_name))

        # check target files
        for target in pipeline.get_targets():
            if not is_file_managed(config, target):
                raise ScmError(f"target file {target} is not tracked by git")
            if is_file_changed(config, target):
                raise ScmError(f"target file {target} is modified. please commit before manipurate")

    def after_process(self, config, pipeline):
        """commit changes"""
        # add changed files
        changed = False
        for target in pipeline.get_targets():
            if is_file_changed(config, target):
                add_file(config, target)
                changed = True
        if not changed:
            logger.info("skip commit - no file changed")
            return
        commit_msg = self.generate_commit_message(pipeline)
        commit(config, commit_msg)
