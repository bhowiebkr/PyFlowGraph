# graph_trust.py
# Decides whether a graph may run code when it opens or is pasted.
#
# Building a node runs its GUI Definition code and its GUI State Handler code, so opening
# a graph file runs code from that file. The editor asks the user first, unless the file
# is a bundled example or the user already trusted this exact file content.

import hashlib
import os

from pyflowgraph.paths import examples_dir

_KEY_PREFIX = "trusted_graphs/"
_MAX_LISTED_NODES = 10


def nodes_with_open_code(data):
    """Return the titles of the nodes whose code runs when the graph is built."""
    titles = []
    nodes = data.get("nodes") if isinstance(data, dict) else None
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        gui_code = node.get("gui_code") or ""
        values_code = node.get("gui_get_values_code") or ""
        if str(gui_code).strip() or str(values_code).strip():
            titles.append(str(node.get("title") or node.get("uuid") or "Untitled node"))
    return titles


def describe_nodes(titles):
    """Return a short list of node titles for a dialog."""
    shown = titles[:_MAX_LISTED_NODES]
    lines = [f"- {title}" for title in shown]
    if len(titles) > len(shown):
        lines.append(f"- and {len(titles) - len(shown)} more")
    return "\n".join(lines)


def content_hash(content):
    """Return the SHA-256 hash of a graph's text."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def _path_key(file_path):
    normalized = os.path.normcase(os.path.realpath(os.path.abspath(file_path)))
    return _KEY_PREFIX + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def bundled_example_dirs():
    """Return the folders that hold the examples shipped with the program."""
    return [examples_dir()]


def is_bundled_example(file_path, example_dirs=None):
    """Return True when the file is inside a folder of shipped examples."""
    real_file = os.path.normcase(os.path.realpath(os.path.abspath(file_path)))
    for folder in example_dirs if example_dirs is not None else bundled_example_dirs():
        if not os.path.isdir(folder):
            continue
        real_folder = os.path.normcase(os.path.realpath(os.path.abspath(folder)))
        try:
            if os.path.commonpath([real_file, real_folder]) == real_folder:
                return True
        except ValueError:
            # Different drives on Windows.
            continue
    return False


class GraphTrustStore:
    """Remembers the graph files that the user trusted, by path and content.

    `settings` is any object with value(key, default) and setValue(key, value), such as
    QSettings. A trusted file that changes on disk is no longer trusted, until the user
    trusts it again or saves it from the editor.
    """

    def __init__(self, settings, example_dirs=None):
        self.settings = settings
        self.example_dirs = example_dirs

    def is_trusted(self, file_path, content):
        if is_bundled_example(file_path, self.example_dirs):
            return True
        saved = self.settings.value(_path_key(file_path), None)
        return bool(saved) and saved == content_hash(content)

    def trust(self, file_path, content):
        self.settings.setValue(_path_key(file_path), content_hash(content))

    def needs_confirmation(self, file_path, content, data):
        """Return the node titles to show the user, or an empty list when no question is needed."""
        titles = nodes_with_open_code(data)
        if not titles or self.is_trusted(file_path, content):
            return []
        return titles
