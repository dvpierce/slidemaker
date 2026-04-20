import argparse
import os
from PIL import Image

class validators:
    @classmethod
    def validate_is_hex(cls, value):
        possible_hex_value = value.lower()
        if possible_hex_value.startswith("#"):
            possible_hex_value = possible_hex_value[1:]
        if len(possible_hex_value) not in [3, 6]:
            raise argparse.ArgumentTypeError(f"{value} is incorrect length for a RGB color code.")
        if not all([character in "0123456789abcdef" for character in possible_hex_value]):
            raise argparse.ArgumentTypeError(f"{value} contains non-hexidecimal characters.")
        return value

    @classmethod
    def validate_is_dir(cls, value):
        if not os.path.isdir(value):
            raise argparse.ArgumentTypeError(f"{value} is not a valid directory path.")
        else:
            return value

    @classmethod
    def validate_is_supported_transition(cls, value):
        if value not in ["0", "1", "2", "3", "4", "fade", "wipe", "push", "ripple", "none"]:
            raise argparse.ArgumentTypeError(f"{value} is not a suported transition type or reference.")
        else:
            return value

    @classmethod
    def validate_is_pilsupported(cls, value):
        pillow_supported_image_types = [ex for ex, f in Image.registered_extensions().items() if f in Image.OPEN]
        if not value.startswith("."):
            value = "." + value
        if value.lower() not in pillow_supported_image_types:
            raise argparse.ArgumentTypeError(f"Extension {value} is not associated with a known or supported image type.")
        else:
            return value