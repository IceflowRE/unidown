"""
Manager of the whole program, contains the most important functions as well as the download routine.
"""
import logging
import multiprocessing
import platform
from pathlib import Path
from typing import List

from unidown import dynamic_data, static_data
from unidown.core import updater
from unidown.core.plugin_state import PluginState
from unidown.plugin.a_plugin import APlugin
from unidown.plugin.exceptions import PluginException
from unidown.tools import create_dir_rec


def init(main_dir: Path, logfile_path: Path, log_level: str):
    """
    Initialize the _downloader. TODO.

    :param main_dir: main directory
    :type main_dir: ~pathlib.Path
    :param logfile_path: logfile path
    :type logfile_path: ~pathlib.Path
    :param log_level: logging level
    :type log_level: str
    """
    dynamic_data.reset()
    dynamic_data.init_dirs(main_dir, logfile_path)

    dynamic_data.check_dirs()

    create_dir_rec(dynamic_data.MAIN_DIR)
    create_dir_rec(dynamic_data.TEMP_DIR)
    create_dir_rec(dynamic_data.DOWNLOAD_DIR)
    create_dir_rec(dynamic_data.SAVESTAT_DIR)
    create_dir_rec(Path.resolve(dynamic_data.LOGFILE_PATH).parent)
    dynamic_data.LOG_LEVEL = log_level
    logging.basicConfig(filename=dynamic_data.LOGFILE_PATH, filemode='a', level=dynamic_data.LOG_LEVEL,
                        format='%(asctime)s.%(msecs)03d | %(levelname)s - %(name)s | %(module)s.%(funcName)s: %('
                               'message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    logging.captureWarnings(True)

    cores = multiprocessing.cpu_count()
    dynamic_data.USING_CORES = min(4, max(1, cores - 1))

    info = f"{static_data.NAME} {static_data.VERSION}\n\n" \
           f"System: {platform.system()} - {platform.version()} - {platform.machine()} - {cores} cores\n" \
           f"Python: {platform.python_version()} - {' - '.join(platform.python_build())}\n" \
           f"Arguments: main={main_dir.resolve()} | logfile={logfile_path.resolve()} | loglevel={log_level}\n" \
           f"Using cores: {dynamic_data.USING_CORES}\n\n"
    with dynamic_data.LOGFILE_PATH.open(mode='w', encoding="utf8") as writer:
        writer.write(info)

    dynamic_data.AVAIL_PLUGINS = APlugin.get_plugins()


def shutdown():
    """
    Close and exit important things.
    """
    logging.shutdown()


def download_from_plugin(plugin: APlugin):
    """
    Download routine.

    1. get newest update time
    2. load savestate
    3. compare last update time with savestate time
    4. get download links
    5. compare with savestate
    6. download new/updated data
    7. check downloads
    8. update savestate
    9. write new savestate

    :param plugin: plugin
    :type plugin: ~unidown.plugin.a_plugin.APlugin
    """
    # get last update date
    plugin.log.info('Get last update')
    plugin.update_last_update()
    # load old save state
    save_state = plugin.load_save_state()
    if plugin.last_update <= save_state.last_update:
        plugin.log.info('No update. Nothing to do.')
        return
    # get download links
    plugin.log.info('Get download links')
    plugin.update_download_links()
    # compare with save state
    down_link_item_dict = plugin.get_updated_data(save_state.link_item_dict)
    plugin.log.info('Compared with save state: ' + str(len(plugin.download_data)))
    if not down_link_item_dict:
        plugin.log.info('No new data. Nothing to do.')
        return
    # download new/updated data
    plugin.log.info(f"Download new {plugin.unit}s: {len(down_link_item_dict)}")
    plugin.download(down_link_item_dict, plugin.download_path, 'Download new ' + plugin.unit + 's', plugin.unit)
    # check which downloads are succeeded
    succeed_link_item_dict, lost_link_item_dict = plugin.check_download(down_link_item_dict, plugin.download_path)
    plugin.log.info(f"Downloaded: {len(succeed_link_item_dict)}/{len(down_link_item_dict)}")
    # update savestate link_item_dict with succeeded downloads dict
    plugin.log.info('Update savestate')
    plugin.update_dict(save_state.link_item_dict, succeed_link_item_dict)
    # write new savestate
    plugin.log.info('Write savestate')
    plugin.save_save_state(save_state.link_item_dict)


def run(plugin_name: str, options: List[str] = None) -> PluginState:
    """
    Run a plugin so use the download routine and clean up after.

    :param plugin_name: name of plugin
    :type plugin_name: str
    :param options: parameters which will be send to the plugin initialization
    :type options: List[str]
    :return: success
    :rtype: ~unidown.plugin.plugin_state.PluginState
    """
    if options is None:
        options = []

    if plugin_name not in dynamic_data.AVAIL_PLUGINS:
        msg = 'Plugin ' + plugin_name + ' was not found.'
        logging.error(msg)
        print(msg)
        return PluginState.NOT_FOUND

    try:
        plugin_class = dynamic_data.AVAIL_PLUGINS[plugin_name].load()
        plugin = plugin_class(options)
    except Exception:
        msg = 'Plugin ' + plugin_name + ' crashed while loading.'
        logging.exception(msg)
        print(msg + ' Check log for more information.')
        return PluginState.LOAD_CRASH
    else:
        logging.info('Loaded plugin: ' + plugin_name)

    try:
        download_from_plugin(plugin)
        plugin.clean_up()
    except PluginException as ex:
        msg = f"Plugin {plugin.name} stopped working. Reason: {'unknown' if (ex.msg == '') else ex.msg}"
        logging.error(msg)
        print(msg)
        return PluginState.RUN_FAIL
    except Exception:
        msg = 'Plugin ' + plugin.name + ' crashed.'
        logging.exception(msg)
        print(msg + ' Check log for more information.')
        return PluginState.RUN_CRASH
    else:
        logging.info(plugin.name + ' ends without errors.')
        return PluginState.END_SUCCESS


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
        print("!!! UPDATE AVAILABLE !!!\n"
              "" + static_data.PROJECT_URL + "\n\n")
        logging.info("Update available: " + static_data.PROJECT_URL)
    else:
        logging.info("No update available.")
