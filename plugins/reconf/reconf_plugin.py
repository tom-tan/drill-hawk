from datetime import datetime

# import sys
# from flask import render_template
from jinja2 import Environment, BaseLoader
from plugins import base

reconf_cell_template = """
{% if step.step_name[0] != '_' %}
<div class="ra_cost_time">
<span class="small_font">TOTAL:</span>
{{ '{:,}'.format(step.reconf_elapsed_sec) }} sec
        </div>
<span class="ra_cost_time">(<span class="small_font">AS:</span>
{{ '{:,}'.format(step.as_elapsed_sec) }} sec
/ <span class="small_font">RA:</span>
{{ '{:,}'.format(step.ra_elapsed_sec) }} sec)</span>
{% elif step.step_name == '_prepare' %}
<span class="ra_cost_time"> <span class="small_font">TOTAL:</span>
{{ '{:,}'.format(content.prepare_elapsed_sec) }} sec</span>
{% else %}
<span class="ra_cost_time"> <span class="small_font">TOTAL:</span>
{{ '{:,}'.format(content.total_reconf_elapsed_sec) }} sec</span>
{% endif %}
"""
jinja2_env = Environment(loader=BaseLoader())


class ASRAFetch(base.DHFetchPlugin):
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

    # pluginとして定義
    def elapsed_sec(self, start_date, end_date):
        """
        end_data - start_date の秒数計算
        """
        start_timestamp = datetime.strptime(start_date[0:19], "%Y-%m-%dT%H:%M:%S")
        end_timestamp = datetime.strptime(end_date[0:19], "%Y-%m-%dT%H:%M:%S")
        elapsed_sec = (end_timestamp - start_timestamp).total_seconds()

        return int(elapsed_sec)

    # TODO: applyはpythonの予約後? 調査する pandadでもapplyは使われているが、
    # TODO; workflow_dataに対するデータ加工なのでgraph.buildに移すのが良さそう(2つに分ける意味が有るか?)
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
            ] = self.elapsed_sec(start_date, end_date)

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
            ] = self.elapsed_sec(start_date, end_date)

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
                ra_elapsed_sec = self.elapsed_sec(ra_start_date, ra_end_date)
                cwl_workflow_data["steps"][step_name]["ra_elapsed_sec"] = ra_elapsed_sec

                # AS Core処理時間 = reconf開始時間 - RA開始時間
                reconf_start_date = val["reconf"]["start_time"]
                as_elapsed_sec = self.elapsed_sec(
                    reconf_start_date, ra_start_date
                )
                cwl_workflow_data["steps"][step_name]["as_elapsed_sec"] = as_elapsed_sec

                cwl_workflow_data["steps"][step_name]["reconf_elapsed_sec"] = (
                    as_elapsed_sec + ra_elapsed_sec
                )

                # グラフ用総reconf時間
                total_reconf_elapsed_sec += as_elapsed_sec + ra_elapsed_sec

            # 完成したworkflow 保存
            cwl_workflow_data["total_reconf_elapsed_sec"] = total_reconf_elapsed_sec

        return cwl_workflow_data


class ASRATable(base.DHTablePlugin):
    def __init__(self):
        pass

    def build(self, workflow_table_data):
        # JSONの値は、HTMLになっている
        # (TODO: データタイプを定義する)
        # TODO: HTMLを出力するのはセルに複数の値を入れることが有るため
        # データを一気に出力形式に変換するのかは微妙。(データ加工と、表現を分けるか)
        # AS/RAの場合はフェッチしたデータに必要な情報が入っているが
        # 入っていない場合は、ここで? フェッチしてSQL JOINのようなことをする。
        # TODO: データの取得(必要な場合)は別にしたほうが良さそう
        # 1. as, raの行の加工
        # 2. 列を追加

        # reconfigure cost column
        # TODO: 条件の見直し {% if step.step_name[0] != '_' %}
        # title, cells
        column_name = "reconfigure cost"
        workflow_table_data["ext_columns"].append(column_name)
        template = jinja2_env.from_string(reconf_cell_template)
        for step in workflow_table_data["steps"]:
            step[column_name] = template.render(step=step, content=workflow_table_data)

        return workflow_table_data


# CREST: graph
class ASRAGraph(base.DHGraphPlugin):
    def __init__(self):
        pass

    # TODO: telegrafのデータを集計したいときはここでする?
    # TODO: workflow_data, graph_dataともに全体を示すことを仮定する
    # TODO: 巨大なデータを扱うときにどうするか?(データベースを介して加工するとか?)
    # TODO: graph_symについて検討
    def build(self, workflow_data, graph_data, steps, total_keys):
        """ グラフのデータをreconf情報をつけて加工し、加工後のデータを返す。

        * prepareとreconfにかかった時間
        * prepareにかかった時間
        * reconfにかかった時間
        """
        wf = workflow_data["workflow"]

        graph_data["prepare_elapsed_sec"] = wf["prepare_elapsed_sec"]
        graph_data["total_reconf_elapsed_sec"] = workflow_data[
            "total_reconf_elapsed_sec"
        ]

        #
        # reconf合計 stepを追加する
        #
        name = "_total_reconf"
        graph_data["id-{}".format(name)] = "{}-01".format(name)
        graph_data["time-{}".format(name)] = workflow_data["total_reconf_elapsed_sec"]
        graph_data["cost-{}".format(name)] = 0
        graph_data["start-{}".format(name)] = ""
        graph_data["end-{}".format(name)] = ""
        # グラフ出力する項目名の設定
        for graph_sym in ["cost", "time"]:
            total_keys.insert(0, "{:02d}-{}-{}".format(2, graph_sym, name))
        steps.insert(0, self.__null_metrics(name))

        #
        # prepare stepを追加する
        #
        name = "_prepare"
        graph_data["id-{}".format(name)] = "{}-01".format(name)
        graph_data["time-{}".format(name)] = wf["prepare_elapsed_sec"]
        graph_data["cost-{}".format(name)] = 0
        graph_data["start-{}".format(name)] = ""
        graph_data["end-{}".format(name)] = ""
        for graph_sym in ["cost", "time"]:
            total_keys.insert(0, "{:02d}-{}-{}".format(1, graph_sym, name))
        steps.insert(0, self.__null_metrics(name))

        return (graph_data, steps, total_keys)

    def __null_metrics(self, stepname):
        return {
            "start_date": "",
            "end_date": "",
            "container": {
                "process": {
                    "image": "",
                    "start_time": "",
                    "end_time": "",
                    "exit_code": 0,
                    "id": stepname,
                    "cmd": None,
                    "status": None,
                }
            },
            "stepname": stepname,
            "step_name": stepname,
            "tool_status": "ok",
            "cwl_file": stepname,
            "platform": {
                "hostname": "",
                "total_memory": 0,
                "ec2_instance_type": "",
                "disk_size": None,
                "ncpu_cores": 0,
                "ec2_ami_id": None,
                "ec2_region": "",
            },
        }


# TODO: プラグインの初期化時に設定値などを渡す仕組み? 案: dictにして渡す?
def create_plugin(*args, **kwargs):
    plugin = base.DHPlugin(fetch=ASRAFetch(), table=ASRATable(), graph=ASRAGraph())
    return plugin
