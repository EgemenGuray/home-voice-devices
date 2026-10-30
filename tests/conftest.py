from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class Tag(str):
    """A YAML tag such as !secret or !include, kept as text so the configs load without ESPHome."""

    def __new__(cls, tag, value):
        obj = super().__new__(cls, value)
        obj.tag = tag
        return obj


class Loader(yaml.SafeLoader):
    pass


def _tag(loader, suffix, node):
    return Tag(suffix, loader.construct_scalar(node))


Loader.add_multi_constructor("!", _tag)


def load(path: Path):
    return yaml.load(path.read_text(), Loader=Loader)
