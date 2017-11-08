"""
Manager of the whole program, contains the most important functions as well as the download routine.
"""
# TODO: more detailed description of the program and how it works.
import importlib
import logging
import multiprocessing
import platform
from pathlib import Path

import unidown.core.data.dynamic as dynamic_data
import unidown.core.data.static as static_data
from unidown.core import updater
from unidown.plugins.a_plugin import APlugin
from unidown.plugins.exceptions import GetDownloadLinksException, LastUpdateException, PluginException
from unidown.tools.tdqm_option import TdqmOption
from unidown.tools.tools import create_dir_rec


def init(main_dir: Path, logfile_path: Path, log_level):
    """
    Init the downloader.
    :param main_dir: main directory
    :param logfile_path: logfile path
    :param log_level: logging level
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

    info = "{name} {version}\n\n" \
           "System: {plat_sys} - {plat_ver} - {plat_mach} - {cores} cores\n" \
           "Python: {py_ver} - {py_build}\n" \
           "Arguments: main={main_dir} | logfile={logfile} | loglevel={loglevel}\n" \
           "Using cores: {ucores}\n\n" \
           "".format(name=static_data.NAME, version=static_data.VERSION, plat_sys=platform.system(), cores=cores,
                     plat_ver=platform.version(), plat_mach=platform.machine(), py_ver=platform.python_version(),
                     py_build=' - '.join(platform.python_build()), main_dir=str(main_dir.resolve()),
                     logfile=str(logfile_path.resolve()), loglevel=log_level, ucores=dynamic_data.USING_CORES)
    with dynamic_data.LOGFILE_PATH.open(mode='w', encoding="utf8") as writer:
        writer.write(info)


def shutdown():
    """
    Closes and exit important things.
    """
    logging.shutdown()


def download_from_module(mod: APlugin):
    """
    Download routine.
    1. get last update time
    2. load savestate
    3. compare last update time with savestate time
    4. get download links
    5. compare with savestate
    6. download new/updated data
    7. check downloads
    8. update savestate
    9. write new savestate
    :param mod: module
    :return: boolean if succeeded
    """
    # get last update date
    try:
        mod.logging.info('Get last update')
        last_update = mod.update_last_update()
    except LastUpdateException as ex:
        mod.logging.error(ex.msg)
        return False
    # load old save state
    save_state = mod.load_save_state()
    if last_update <= save_state.last_update:
        mod.logging.info('No update. Nothing to do.')
        return True
    # get download links
    try:
        mod.logging.info('Get download links')
        new_link_item_dict = mod.get_download_links()
    except GetDownloadLinksException as ex:
        logging.error(ex.msg)
        return False
    # compare with save state
    down_link_item_dict = mod.compare_old_with_new_data(save_state.link_linkitem, new_link_item_dict)
    mod.logging.info('Compared with save state: ' + str(len(new_link_item_dict)))
    if not down_link_item_dict:
        mod.logging.info('No new data. Nothing to do.')
        return True
    # download new/updated data
    mod.logging.info('Download new {unit}s: {number}'.format(unit=mod.unit, number=len(down_link_item_dict)))
    mod.download(down_link_item_dict, mod.download_path, TdqmOption('Download new ' + mod.unit + 's', mod.unit))
    # check which downloads are succeeded
    succeed_link_item_dict, lost_link_item_dict = mod.check_download(down_link_item_dict, mod.download_path)
    mod.logging.info(
        'Downloaded: {success}/{total}'.format(success=len(succeed_link_item_dict), total=len(down_link_item_dict)))
    # update savestate link_item_dict with succeeded downloads dict
    mod.logging.info('Update savestate')
    mod.update_dict(save_state.link_linkitem, succeed_link_item_dict)
    # write new savestate
    mod.logging.info('Write savestate')
    mod.save_save_state(save_state.link_linkitem)
    return True


def run(plugin_list):
    """
    Run through a list of module names, init_dirs and use the download routine each.
    :param plugin_list: names of modules
    """
    for plugin_name in plugin_list:
        try:
            logging.info('Loading plugin: ' + plugin_name)
            cur_module = importlib.import_module('unidown.plugins.{name}.plugin'.format(name=plugin_name))
            plugin_class = getattr(cur_module, 'Plugin')
            plugin = plugin_class()
            logging.info('Loaded plugin: ' + plugin_name)
            result = download_from_module(plugin)
            if result:
                logging.info(plugin.name + ' ends without errors.')
            else:
                logging.error(plugin.name + ' ends with errors.')
            # clean up
            plugin.clean_up()
            del plugin, plugin_class
        except PluginException as ex:
            logging.exception(ex.msg)
            print('Plugin {plugin_name} stopped working. Reason: {reason}'.format(plugin_name=plugin_name,
                                                                                  reason='unknown' if (
                                                                                      ex.msg == '') else ex.msg))
        except ImportError:
            msg = 'Plugin ' + plugin_name + ' was not found.'
            logging.error(msg)
            print(msg)
        except Exception:
            msg = 'Plugin ' + plugin_name + ' crashed.'
            logging.exception(msg)
            print(msg + ' Check log for more information.')


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
