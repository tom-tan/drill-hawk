
import importlib
import yaml


def load(dh_config_file):
    with open(dh_config_file) as f:
        dh_config = yaml.safe_load(f)

    # TODO: 順番を表とグラフで異なるように制御したい?
    plugin_path_list = dh_config["plugins"]
    plugin_list = []
    for plugin_path in plugin_path_list:
        m = importlib.import_module("plugins.{}".format(plugin_path))
        plugin_list.append(m.create_plugin())
    return plugin_list
