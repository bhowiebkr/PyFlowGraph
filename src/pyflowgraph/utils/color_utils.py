# color_utils.py
# A utility for generating consistent, bright colors from arbitrary strings.

import hashlib
from PySide6.QtGui import QColor

# A cache to store generated colors so we don't have to re-hash every time.
COLOR_CACHE = {}


def generate_color_from_string(type_str: str) -> QColor:
    """
    Generates a consistent, bright QColor from a given string (e.g., a type hint).

    This function uses a hashing algorithm to ensure the same string always
    produces the same color. The hash is then used to generate HSV values
    that are constrained to a bright and colorful range.

    :param type_str: The string to generate a color for.
    :return: A QColor instance.
    """
    type_str = type_str.lower()

    if type_str in COLOR_CACHE:
        return COLOR_CACHE[type_str]

    # Special case for a generic 'any' type for reroute nodes, etc.
    if type_str == "any":
        color = QColor("#C0C0C0")  # Grey
        COLOR_CACHE[type_str] = color
        return color

    # Use SHA1 to get a consistent hash from the string
    hash_object = hashlib.sha1(type_str.encode("utf-8"))
    hex_digest = hash_object.hexdigest()

    # Use parts of the hash to determine Hue, Saturation, and Value
    # We use integer conversion on slices of the hex hash string

    # Hue: Full 360-degree range for variety
    hue = int(hex_digest[:4], 16) % 360

    # Saturation: Constrained to be high (180-255) to avoid dull colors
    saturation = 180 + (int(hex_digest[4:8], 16) % 76)

    # Value: Constrained to be high (200-255) to avoid dark colors
    value = 200 + (int(hex_digest[8:12], 16) % 56)

    color = QColor.fromHsv(hue, saturation, value)
    COLOR_CACHE[type_str] = color

    return color
