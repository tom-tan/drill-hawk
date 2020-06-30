from datetime import datetime


class ASRAFetch(object):
    def __init__(self):
        pass

    def get_es_source(self):
        """ メトリクスのElasticSearchでデータをsearchするときに、
        _sourcesに指定する項目を返す
        """
        return [
            "workflow.prepare.*",
            "steps.*.reconf.*",
        ]

    def workflow_elapsed_sec(self, start_date, end_date):
        """
        end_data - start_date の秒数計算
        """
        start_timestamp = datetime.strptime(start_date[0:19], "%Y-%m-%dT%H:%M:%S")
        end_timestamp = datetime.strptime(end_date[0:19], "%Y-%m-%dT%H:%M:%S")
        workflow_elapsed_sec = (end_timestamp - start_timestamp).total_seconds()

        return int(workflow_elapsed_sec)

    # TODO: applyはpythonの予約後? 調査する pandadでもapplyは使われているが、
    def build(self, cwl_workflow_data):
        """ AS, RAの処理時間の情報を計算して、cwl_workflow_dataに格納する
        :return: 情報追加した cwl_workflow_data
        """
        # (TODO: データタイプを定義する)
        # TODO: HTMLを出力するのはセルに複数の値を入れることが有るため
        # データを一気に出力形式に変換するのかは微妙。(データ加工と、表現を分けるか)
        # AS/RAの場合はフェッチしたデータに必要な情報が入っているが
        # 入っていない場合は、ここで? フェッチしてSQL JOINのようなことをする。　
        # TODO: データの取得(必要な場合)は別にしたほうが良さそう
        # 副作用を起こしつつ、起こしたデータを返す
        """ テーブルのセルを加工し、HTML(要検討)を出力する
        """

        # prepare step計算
        cwl_workflow_data["workflow"]["prepare_elapsed_sec"] = 0
        if "prepare" in cwl_workflow_data["workflow"]:
            start_date = cwl_workflow_data["workflow"]["prepare"]["start_time"]
            end_date = cwl_workflow_data["workflow"]["prepare"]["end_time"]
            cwl_workflow_data["workflow"][
                "prepare_elapsed_sec"
            ] = self.workflow_elapsed_sec(start_date, end_date)

        # reconf 時間は、workflow全体分をグラフ表示
        total_reconf_elapsed_sec = 0

        # assert len(cwl_workflow_data) == 1

        # prepare step計算
        cwl_workflow_data["workflow"]["prepare_elapsed_sec"] = 0
        if "prepare" in cwl_workflow_data["workflow"]:
            start_date = cwl_workflow_data["workflow"]["prepare"]["start_time"]
            end_date = cwl_workflow_data["workflow"]["prepare"]["end_time"]
            cwl_workflow_data["workflow"][
                "prepare_elapsed_sec"
            ] = self.workflow_elapsed_sec(start_date, end_date)

        # reconf 時間は、workflow全体分をグラフ表示
        total_reconf_elapsed_sec = 0
        for step_name, val in cwl_workflow_data["steps"].items():
            # reconf 時間初期化
            cwl_workflow_data["steps"][step_name]["reconf_elapsed_sec"] = 0
            cwl_workflow_data["steps"][step_name]["as_elapsed_sec"] = 0
            cwl_workflow_data["steps"][step_name]["ra_elapsed_sec"] = 0
            # reconf 時間
            if "reconf" in val:
                # RA 時間
                ra_start_date = val["reconf"]["ra"]["start_time"]
                ra_end_date = val["reconf"]["ra"]["end_time"]
                ra_elapsed_sec = self.workflow_elapsed_sec(
                    ra_start_date, ra_end_date
                )
                cwl_workflow_data["steps"][step_name][
                    "ra_elapsed_sec"
                ] = ra_elapsed_sec

                # AS Core処理時間 = reconf開始時間 - RA開始時間
                reconf_start_date = val["reconf"]["start_time"]
                as_elapsed_sec = self.workflow_elapsed_sec(
                    reconf_start_date, ra_start_date
                )
                cwl_workflow_data["steps"][step_name][
                    "as_elapsed_sec"
                ] = as_elapsed_sec

                cwl_workflow_data["steps"][step_name][
                    "reconf_elapsed_sec"
                ] = as_elapsed_sec + ra_elapsed_sec

                # グラフ用総reconf時間
                total_reconf_elapsed_sec += (as_elapsed_sec + ra_elapsed_sec)

            # 完成したworkflow 保存
            cwl_workflow_data["total_reconf_elapsed_sec"] = total_reconf_elapsed_sec

        return cwl_workflow_data


# CREST: table
# TODO: ベーククラスの定義
class ASRATable(object):
    def __init__(self):
        pass

    def apply(self, workflow_data, table_data):
        # (TODO: データタイプを定義する)
        # TODO: HTMLを出力するのはセルに複数の値を入れることが有るため
        # データを一気に出力形式に変換するのかは微妙。(データ加工と、表現を分けるか)
        # AS/RAの場合はフェッチしたデータに必要な情報が入っているが
        # 入っていない場合は、ここで? フェッチしてSQL JOINのようなことをする。　
        # TODO: データの取得(必要な場合)は別にしたほうが良さそう
        """ テーブルのセルを加工し、HTML(要検討)を出力する
        """
        return table_data


# CREST: graph
# TODO: ベーククラスの定義
class ASRAGraph(object):
    def __init__(self):
        pass

    def apply(self, workflow_data, graph_data):
        # TODO: telegrafのデータを集計したいときはここでする?
        # TODO: workflow_data, graph_dataともに全体を示すことを仮定する
        # TODO: 巨大なデータを扱うときにどうするか?(データベースを介して加工するとか?)
        """ グラフのデータを加工し、加工後のデータを返す。
        """
        # TODO: ASRAでは左橋に時間隠るようにする
        return graph_data


# TODO コードを移動
class DHPlugin(object):
    def __init__(self,
                 fetch=None,
                 table=None,
                 graph=None):
        self.fetch = fetch
        self.table = table
        self.graph = graph


# TODO: プラグインの初期化時に設定値などを渡す仕組み? 案: dictにして渡す?
def create_plugin(*args, **kwargs):
    plugin = DHPlugin(
        fetch=ASRAFetch(),
        table=ASRATable(),
        graph=ASRAGraph())
    return plugin
