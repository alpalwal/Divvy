from DivvyPlugins.plugin_metadata import PluginMetadata
from DivvyPlugins.settings import GlobalSetting
from DivvyResource.Resources import DivvyPlugin


class metadata(PluginMetadata):
    """
    Information about this plugin
    """
    version = '1.0'
    last_updated_date = '2015-08-05'
    author = 'DivvyCloud Inc.'
    nickname = 'Discover filters'
    default_language_description = (
        'Contains custom filters for Discover.'
    )
    support_email = 'support@divvycloud.com'
    support_url = 'http://support.divvycloud.com'
    main_url = 'http://www.divvycloud.com'
    managed = True


def load():
    pass


def unload():
    pass
