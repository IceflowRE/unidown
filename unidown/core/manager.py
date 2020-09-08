"""
Manager of the whole program, contains the most important functions as well as the download routine.
"""
import logging
import multiprocessing
import platform
from typing import List, Dict, Any

from unidown import static_data, tools
from unidown.core import updater
from unidown.core.plugin_state import PluginState
from unidown.core.settings import Settings
from unidown.plugin.a_plugin import APlugin
from unidown.plugin.exceptions import PluginException
from unidown.plugin.link_item_dict import LinkItemDict


def init_logging(settings: Settings):
    """
    Initialize the _downloader.

    :param settings: settings
    """
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(settings.log_file), filemode='a', level='DEBUG',
        format='%(asctime)s.%(msecs)03d | %(levelname)s - %(name)s | %(module)s.%(funcName)s: %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S'
    )
    logging.captureWarnings(True)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)s - %(name)s | %(message)s', datefmt='%Y.%m.%d %H:%M:%S'))
    console_handler.setLevel(settings.log_level)
    logging.getLogger().addHandler(console_handler)

    info = f"{static_data.NAME} {static_data.VERSION}\n\n" \
           f"System: {platform.system()} - {platform.version()} - {platform.machine()} - {multiprocessing.cpu_count()} cores\n" \
           f"Python: {platform.python_version()} - {' - '.join(platform.python_build())}\n" \
           f"Arguments: main={settings.root_dir.resolve()} | logfile={settings.log_file} | loglevel={settings.log_level}\n" \
           f"Using cores: {settings.cores}\n"

    logging.debug(info)


def shutdown():
    """
    Close and exit important things.
    """
    logging.shutdown()


def download_from_plugin(plugin: APlugin):
    """
    Download routine.

    1. Get plugin from the given name
    2. Get the last overall update time
    3. Load the savestate
    4. Compare last update time with the one from the savestate
    5. Get the download links
    6. Compare received links and their times with the savestate
    7. Clean up names, to eliminate duplicated
    8. Download new and newer links
    9. Check downloaded data
    10. Update savestate
    11. Save new savestate to file

    :param plugin: plugin
    """
    # get last update date
    plugin.log.info('Get last update')
    plugin.update_last_update()
    # load old save state
    plugin.load_savestate()
    if plugin.last_update <= plugin.savestate.last_update:
        plugin.log.info('No update. Nothing to do.')
        return
    # get download links
    plugin.log.info('Get download links')
    plugin.update_download_data()
    # compare with save state
    new_items = LinkItemDict.get_new_items(plugin.savestate.link_items, plugin.download_data)
    plugin.log.info(f"Compared with save state: {str(len(plugin.download_data))}")
    if len(new_items) == 0:
        plugin.log.info('No new data. Nothing to do.')
        return
    # clean up saving names
    plugin.log.info("Clean up names.")
    new_items.clean_up_names()
    # download new/updated data
    plugin.log.info(f"Download new {plugin.unit}s: {len(new_items)}")
    plugin.download(new_items, plugin.download_dir, f"Download new {plugin.unit}s", plugin.unit)
    # check which downloads are succeeded
    succeeded, _ = plugin.check_download(new_items, plugin.download_dir)
    plugin.log.info(f"Downloaded: {len(succeeded)}/{len(new_items)}")
    # update savestate link_item_dict with succeeded downloads dict
    plugin.log.info('Update savestate')
    plugin.update_savestate(succeeded)
    # write new savestate
    plugin.log.info('Write savestate')
    plugin.save_savestate()


def run(settings: Settings, plugin_name: str, raw_options: List[List[str]]) -> PluginState:
    """
    Run a plugin so use the download routine and clean up after.

    :param settings: settings to use
    :param plugin_name: name of plugin
    :param raw_options: parameters which will be send to the plugin initialization
    :return: ending state
    """
    if raw_options is None:
        options = {}
    else:
        options = get_options(raw_options)

    available_plugins = APlugin.get_plugins()
    if plugin_name not in available_plugins:
        msg = f"Plugin {plugin_name} was not found."
        logging.error(msg)
        return PluginState.NotFound

    # delete temporary directory of the plugin
    tools.unlink_dir_rec(settings.temp_dir.joinpath(plugin_name))
    try:
        plugin_class = available_plugins[plugin_name].load()
        plugin = plugin_class(settings, options)
    except Exception:
        logging.exception(f"Plugin {plugin_name} crashed while loading.")
        return PluginState.LoadCrash
    else:
        logging.info(f"Loaded plugin: {plugin_name}")

    try:
        download_from_plugin(plugin)
        plugin.clean_up()
    except PluginException:
        logging.exception(f"Plugin {plugin.name} stopped working.")
        return PluginState.RunFail
    except Exception:
        logging.exception(f"Plugin {plugin.name} crashed.")
        return PluginState.RunCrash
    else:
        logging.info(f"{plugin.name} ends without errors.")
        return PluginState.EndSuccess


def get_options(options: List[List[str]]) -> Dict[str, Any]:
    """
    Convert the option list to a dictionary where the key is the option and the value is the related option.
    Is called in the init.

    :param options: options given to the plugin.
    :return: dictionary which contains the option key and values
    """
    plugin_options = {}
    for sub_options in options:
        option = ' '.join(sub_options)
        option_key, _, option_value = option.partition('=')

        if option_key == '' or option_value == '':
            logging.warning(f"'{option}' is not valid and will be ignored.")
            continue
        plugin_options[option_key] = option_value
    return plugin_options


def check_update():
    """
    Check for app updates and print/log them.
    """
    logging.info('Check for app updates.')
    try:
        update = updater.check_for_app_updates()
    except Exception:
        logging.exception('Check for updates failed.')
        return
    if update:
        logging.info(f"Update available! ({static_data.PROJECT_URL})")
    else:
        logging.info("No update available.")
