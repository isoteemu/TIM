import subprocess

def get_current_commit_sha() -> str:
    """Get the current git commit SHA."""
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE
            )
            .stdout.decode()
            .strip()
        )
    except:  # noqa: E722
        return ""


def is_dirty() -> bool:
    """Check if the git repository is dirty."""
    try:
        return bool(
            subprocess.run(
                ["git", "status", "--porcelain"], stdout=subprocess.PIPE
            )
            .stdout.decode()
            .strip()
        )
    except:  # noqa: E722
        return False


def get_version_info() -> str:
    """Get the current git commit SHA and dirty status."""
    sha = get_current_commit_sha()
    dirty = is_dirty()
    if dirty:
        sha += "-dirty"
    return sha
