# TODO: overrideデコレータを定義


class DHFetchPlugin(object):
    def get_es_source(self):
        """ メトリクスのElasticSearchでデータをsearchするときに、
        _sourcesに指定する項目のリストを返す

        :return: _sourcesに指定する項目のリスト (string list)
        """
        raise NotImplementedError()

    def build(self, cwl_workflow_data):
        """ cwl_workflow_dataにプラグインが必要とするデータを追加する。

        :param cwl_workflow_data: メトリクスのElasticSearchから取得したworkflow情報
        :return: 情報追加した cwl_workflow_data
        """
        raise NotImplementedError()


class DHGraphPlugin(object):
    def build(self, graph_sym, workflow_data, graph_data, steps, total_keys):
        """ グラフデータにプラグインが付加したいデータを追加する。

        :param graph_sym:
        :param workflow_data:
        :param graph_data:
        :param steps:
        :param total_keys:

        :return: 加工後の graph_data, steps, total_keys のtuple
        """
        raise NotImplementedError()


class DHTablePlugin(object):
    def build(self, workflow_table_data):
        """ テーブルのセルを加工し、HTML(TODO 要検討)を出力する

        :return: 加工後の workflow_table_data (dict)
        """
        raise NotImplementedError()


# TODO: 空のプラグインを追加してNoneが来たときにそれをセットする?
# 暫定版
class DHPlugin(object):
    def __init__(
        self, fetch=None, table=None, graph=None  # DHFetchPlugin  # DHTablePlugin
    ):  # DHGraphPlugin
        self.fetch = fetch
        self.table = table
        self.graph = graph
