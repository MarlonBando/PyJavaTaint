import os

def get_full_path(relative_path: str) -> str:
    """
    Returns the absolute path given a relative path starting from the project directory.

    Args:
        relative_path (str): The relative path from the project directory.

    Returns:
        str: The absolute path.
    """
    project_dir = os.path.dirname(__file__)
    project_dir = os.path.dirname(os.path.dirname(project_dir))
    return os.path.abspath(os.path.join(project_dir, relative_path))