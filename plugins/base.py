
#TODO： ドキュメント
# - 処理順序
#   classの順序
#   pluginの順序


class DHFetchPlugin(object):
    """ Drill-Hawkプラグイン

    """

    def get_es_source(self):
        """ メトリクスのElasticSearchでデータをsearchするときに、
        _sourceに指定する項目のリストを返す

        :return: _sourcesに指定するElasticSearch上の項目のリスト (string list)
        """
        raise NotImplementedError()

    def build(self, cwl_workflow_data):
        """ cwl_workflow_dataにプラグインが必要とするデータを追加する。

        :param cwl_workflow_data: メトリクスのElasticSearchから取得したworkflow情報
        :return: 引数のcwl_workflow_dataに情報追加したデータ。

        .. note::
            cwl_workflow_data の標準は、以下のドキュメントを参照

            <https://github.com/inutano/cwl-metrics/tree/master/docs>

            cwl_workflow_data の例は以下の通りである。

            .. code-block:: none
               :linenos:

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

        graph_dataには以下のプレフィックスをステップ名につけたものをキーとして、
        グラフ化するデータ(実行時間、利用料金)が入っている。

        * ``id-`` : ステップ名
        * ``time-`` : 実行時間(秒)
        * ``cost-`` : 利用料金(USD)
        * ``start-`` : 開始時刻
        * ``end-`` : 終了時刻

        :param workflow_data: DHFetchPluginで処理した後のデータ
        :param graph_data: グラフ(d3)用データ
        :param steps: ステップごとのデータ
        :param total_keys: 全てのworkflowで出現するステップをソートしたリスト

        :return: 加工後の (graph_data, steps, total_keys)
        """
        raise NotImplementedError()


class DHTablePlugin(object):
    def build(self, workflow_table_data):
        """ テーブルのセルを加工し、セルごとにHTMLデータに変換する。

        workflow_table_data["ext_columns"] にプラグインでの追加カラムを入れること
        各カラムの値はstepにカラム名のフィールドを追加し、そこに入れること。

        .. code-block:: python
           :linenos:

           workflow_table_data["ext_columns"].append(column_name)
           template = jinja2_env.from_string(reconf_cell_template)
           for step in workflow_table_data["steps"]:
               step[column_name] = template.render(step=step, content=workflow_table_data)

        :param workflow_table_data: テーブル化する対象のデータ
        :return: 加工後の workflow_table_data (dict)
        """

        raise NotImplementedError()


class DHPlugin(object):
    """ pluginのpythonモジュールに ``create_plugin(*args, **kwargs)`` を定義し
    その関数でpluginインスタンスを返すように実装すること。

    .. code-block:: python
       :linenos:

       def create_plugin(*args, **kwargs):
           plugin = base.DHPlugin(fetch=FetchPlugin(),
                                  table=TablePlugin(),
                                  graph=GraphPlugin())
           return plugin

    """

    def __init__(self, fetch=None, table=None, graph=None):
        """ Pluginのインスタンスを返す

        :params fetch: DHFetchPluginのインスタンス
        :params table: DHFTablePluginのインスタンス
        :params graph: DHGraphPluginのインスタンス
        """
        self.fetch = fetch
        self.table = table
        self.graph = graph
