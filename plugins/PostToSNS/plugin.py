"""
Main plugin module for custom filters
"""
from DivvyPlugins.plugin_metadata import PluginMetadata
from DivvyResource.Resources import DivvyPlugin

class metadata(PluginMetadata):
    """
    Information about this plugin
    """
    version = '1.0'
    last_updated_date = '2019-05-17'
    author = 'DivvyCloud'
    nickname = 'Post to SNS bot'
    default_language_description = 'Contains custom actions for Bots'
    category = 'Plugins'
    managed = False


def load():
    pass

def unload():
    pass
