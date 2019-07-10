"""
Main plugin module for custom actions
"""
from DivvyPlugins.plugin_metadata import PluginMetadata


class metadata(PluginMetadata):
    """
    Information about this plugin
    """
    version = '1.0'
    last_updated_date = '2019-07-09'
    author = 'Customer'
    nickname = 'AWS SNS Publish'
    default_language_description = 'Custom Actions & Filters for Customer'
    managed = False


def load():
    pass


def unload():
    pass
