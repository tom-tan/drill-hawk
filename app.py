# -*- coding: utf-8 -*-
# Copyright 2020 National Institute of Informatics
# SPDX-License-Identifier: Apache-2.0
"""
 DrillHawk
"""

from flask import Flask, render_template, request, redirect
from models.cwl_metrics import CwlMetrics
from models.graph import Graph
import os
import json
from plugins import loader

#
# Flask Initialize
#
app = Flask(__name__, static_url_path="/dh")
app.config["DEBUG"] = True
plugins = []

#
# load configure
#
_config = {}
if "ES_ENDPOINT" in os.environ:
    _config["es_endpoint"] = os.environ["ES_ENDPOINT"]

if "ES_INDEX_NAME" in os.environ:
    _config["es_index_name"] = os.environ["ES_INDEX_NAME"]


def url_for_static(filename):
    root = app.config.get("STATIC_ROOT", "")
    return "".join(root, filename)


@app.route("/")
def index():
    return redirect("/dh")


@app.route("/dh/")
def workflows():
    """
    ワークフロー一覧
    """

    # 検索条件
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    keyword1 = request.args.get("keyword1")
    if keyword1 is None:
        keyword1 = ""
    keyword2 = request.args.get("keyword2")
    if keyword2 is None:
        keyword2 = ""
    keyword3 = request.args.get("keyword3")
    if keyword3 is None:
        keyword3 = ""

    #
    # ElasticSearchから検索対象のworkflowを抽出
    #
    cwl = CwlMetrics(_config["es_endpoint"], _config["es_index_name"], plugins)
    recs = cwl.search(from_date, to_date, list(set([keyword1, keyword2, keyword3])))

    return render_template(
        "index.html",
        contents=recs,
        keyword1=keyword1,
        keyword2=keyword2,
        keyword3=keyword3,
        from_date=from_date,
        to_date=to_date,
    )


@app.route("/dh/show", methods=["GET"])
def show_content():
    """
    グラフ
    """

    #
    # ElasticSearchから検索対象のworkflowを抽出
    #
    workflow_ids = request.args.get("workflow_id")
    graph_type = request.args.get("type")

    # cwl metrics 初期化
    cwl = CwlMetrics(_config["es_endpoint"], _config["es_index_name"], plugins)
    # graph data モデル初期化
    graph = Graph(cwl, graph_type, plugins)

    for workflow_id in list(set(workflow_ids.split(","))):
        #
        # ElasticSearch から指定workflowの情報を抽出
        #
        # workflow_id = workflow.cwl_file
        workflow_data = cwl.search_simple(workflow_id)
        app.logger.debug("workflow_data: {}".format(workflow_data))
        if workflow_data is None:
            continue

        #
        # cwl-metrics形式jsonから、workflow 表示用モデルを構築する
        #
        graph.build(workflow_data)
        # TODO; graphの処理をplugin化する?
        # for plugin in plugins:
        # TODO:　データ加工というクラス名にする, fetchと重複する部分が有る
        # plugins.graph.build(graph.data,)

    workflows = []
    for workflow_table_data in graph.workflows:
        # pn(...(p3(p2(p1(w)))))
        workflow_table_data["ext_columns"] = []
        for plugin in plugins:
            workflow_table_data = plugin.table.build(workflow_table_data)
        workflows.append(workflow_table_data)

    app.logger.debug("worfkflows: {}".format(workflows))

    # json形式に変換
    json_data = json.dumps(graph.data, ensure_ascii=False, indent=4, sort_keys=True)

    # total_keys を tool_id でuniq
    total_keys_with_number = sorted(graph.total_keys)

    total_keys = []
    for k in total_keys_with_number:
        key_name = k[3:]
        if key_name not in total_keys:
            total_keys.append(key_name)

    # cost, time のそれぞれのグラフに表示するキーを抽出
    cost_total_keys = []
    time_total_keys = []
    for key in total_keys:
        if "cost" in key:
            cost_total_keys.append(key)
        elif "time" in key:
            time_total_keys.append(key)
    # toggle url
    toggle_url = "./show?type={}&workflow_id={}".format(
        graph.other["graph_type"], workflow_ids
    )

    return render_template(
        "show_content.html",
        graph_type=graph_type,
        graph_name=graph.graph_name,
        graph_unit=graph.graph_unit,
        graph_other=graph.other,
        graph_other_url=toggle_url,
        contents=workflows,
        data=json_data,
        cost_keys=str(cost_total_keys),
        time_keys=str(time_total_keys),
    )


if __name__ == "__main__":
    # TODO: config path
    plugins = loader.load("./dh_config.yml")
    app.run(host="0.0.0.0")
