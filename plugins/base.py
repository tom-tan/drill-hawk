
class DHFetchPlugin(object):
    def get_es_source(self):
        """ メトリクスのElasticSearchでデータをsearchするときに、
        _sourcesに指定する項目のリストを返す

        :return: _sourcesに指定するElasticSearch上の項目のリスト (string list)
        """
        raise NotImplementedError()

    def build(self, cwl_workflow_data):
        """ cwl_workflow_dataにプラグインが必要とするデータを追加する。

        :param cwl_workflow_data: メトリクスのElasticSearchから取得したworkflow情報
        :return: 情報追加した cwl_workflow_data

        .. note::
            cwl_workflow_data の標準は、以下のドキュメントを参照

            <https://github.com/inutano/cwl-metrics/tree/master/docs>

            本reconf plugin は、以下の仕様追加項目がcwl_workflow_data に設定される前提

            - .prepare ... 再構成用前処理
            - .steps[`step_name`].reconf ... 再構成用各step前処理

            args cwl_workflow_data ex.
            ---
            {'workflow':
              {
               'prepare': {
                 'start_time': '2020-05-05T14:22:15',
                 'end_date': '2020-05-05T15:06:28',
                 'end_time': '2020-05-05T14:22:22'
               },
               ...
               'steps': {
                 'HISAT2-3': {
                   'stepname': 'HISAT2-3',
                   'start_date': '2020-05-05T14:24:37',
                   'end_date': '2020-05-05T14:54:06',
                   'reconf': {
                     'start_time': '2020-05-05T14:22:23',
                     'end_time': '2020-05-05T14:24:36',
                     'ra': {'start_time': '2020-05-05T14:22:23.409770',
                     'end_time': '2020-05-05T14:24:29.092136'}
                   },
                 },
                 ...
        """
        raise NotImplementedError()


class DHGraphPlugin(object):
    def build(self, workflow_data, graph_data, steps, total_keys):
        """ グラフデータにプラグインが付加したいデータを追加する。

        TODO: graph_dataの説明を入れる
        TODO: タイムゾーンは?(メトリクスに入っているタイムゾーンは?)

        * ``id-`` : ステップ名 (TODO: 確認)
        * ``time-`` : 実行時間(秒)
        * ``cost-`` : 利用料金(USD)
        * ``start-`` : 開始時刻
        * ``end-`` : 終了時刻

        :param workflow_data:
        :param graph_data:
        :param steps:
        :param total_keys:

        :return: 加工後の graph_data, steps, total_keys のtuple
        """
        # TODO: graphという名前を考え直す
        # graphとあるが、表でもデータを共有する(stepを足しただけ)
        # 単なるデータの変換、DHFetchPlugin.build と区別する必要はなさそう
        raise NotImplementedError()


class DHTablePlugin(object):
    def build(self, workflow_table_data):
        """ テーブルのセルを加工し、HTML(TODO 要検討)を出力する

        workflow_table_data["ext_columns"] にプラグインでの追加カラムを入れること
        各カラムの値はstepにカラム名のフィールドを追加し、そこに入れること::

          workflow_table_data["ext_columns"].append(column_name)
          template = jinja2_env.from_string(reconf_cell_template)
          for step in workflow_table_data["steps"]:
              step[column_name] = template.render(step=step, content=workflow_table_data)

        :param workflow_table_data: テーブル化する対象のデータ
        :return: 加工後の workflow_table_data (dict)
        """
        # TODO: 表の行を足すときはstepに足す。
        # -> stepでないものは入れるべきではない
        # (stepとしてのデータをデフォルトで描画するが、それをカスタマイズするすべを作っていないため)
        # reconfの場合は、prepare, reconfともにgalaxyのstepであるため入れた

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
