import importlib
import yaml


# pluginが不要な場合に呼ぶ?
def load_emply():
    return []


def load(config_path=None):
    with open(config_path) as f:
        dh_config = yaml.safe_load(f)

    plugin_path_list = dh_config.get("plugins")
    if plugin_path_list is None:
        plugin_path_list = []
    plugin_list = []
    for plugin_path in plugin_path_list:
        m = importlib.import_module("plugins.{}".format(plugin_path))
        plugin_list.append(m.create_plugin())
    return plugin_list
