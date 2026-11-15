"""Folders that the editor uses, found from the location of this package.

The results do not depend on the current working folder.
"""

import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# The folder that holds the package: src/ in a checkout, the program folder in the Windows build.
APP_DIR = os.path.dirname(PACKAGE_DIR)


def project_dir():
    """Return the folder that holds examples/ and venvs/.

    In a checkout this is the repository root, the parent of src/. Nuitka sets __compiled__ in
    the Windows build, where examples/ is next to the program.
    """
    if "__compiled__" in globals():
        return APP_DIR
    return os.path.dirname(APP_DIR)


def examples_dir():
    """Return the folder of the examples shipped with the program."""
    return os.path.join(project_dir(), "examples")


def default_venv_parent_dir():
    """Return the default folder for the graph virtual environments."""
    return os.path.join(project_dir(), "venvs")
