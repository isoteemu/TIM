import subprocess
from functools import lru_cache


def try_fix_safe_dir_config() -> None:
    try:
        subprocess.run(
            [
                "git",
                "config",
                "--global",
                "--add",
                "safe.directory",
                "/service",
            ]
        )
    except:
        print(
            "Could not fix safe.directory config; some git commands will not work. "
            "Make sure global git config is editable."
        )
        pass


# Ensure the main dir is marked as safe
# See https://github.blog/2022-04-12-git-security-vulnerability-announced/
try_fix_safe_dir_config()


def get_latest_commit_timestamp() -> str:
    try:
        return (
            subprocess.run(
                ["git", "log", "-1", "--date=format:%d.%m.%Y %H:%M:%S", "--format=%cd"],
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
        )
    except:
        return "<detached>"


def get_current_branch() -> str:
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE
            )
            .stdout.decode()
            .strip()
        )
    except:
        return "<detached>"


@lru_cache(maxsize=1)
def is_dirty() -> bool:
    """
    Check if the git repository is dirty – i.e., has uncommitted changes.

    Note: The result is cached for the lifetime of the process.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], stdout=subprocess.PIPE
        )
        output = result.stdout.decode().strip()
        return len(output) > 0
    except:  # noqa: E722
        return False
