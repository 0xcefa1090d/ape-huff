from ape import plugins

from ape_huff.compiler import HuffConfig


@plugins.register(plugins.Config)
def config_class():
    return HuffConfig
