# -*- coding: utf-8 -*-
# Copyright 2020 National Institute of Informatics
# SPDX-License-Identifier: Apache-2.0

from elasticsearch import Elasticsearch
import utils.dh_util as dh_util
# import json


class CwlMetrics:
    def __init__(self, elastic_search_endpoint, index_name, plugins, cells=None):
        # TODO: index_nameはworkflowデータの?
        """ CwlMetricsを取得するクライアント

        :param elastic_search_endpoint: ElasticSearchのエンドポイント(IPアドレス、ホスト名とポート番号を:で区切ったもの)
        :param index_name: ElasticSearch上のindex名
        :param plugins: Drill-Hawkのプラグインのリスト
        :param cells: ElasticSearch上の検索対象のindex名
        """

        #
        # 検索対象のindex名
        #
        if cells is None:
            self.cells = [
                "workflow.cwl_file",
                "workflow.inputs.filename",
                "workflow.outputs.filename",
                "steps.keyword",
            ]
        else:
            self.cells = cells
        #
        # generate query
        #
        self.source = [
            "cwl_metrics_version",
            "workflow.start_date",
            "workflow.end_date",
            "workflow.cwl_file",
            "workflow.inputs.*",
            "steps.*.start_date",
            "steps.*.end_date",
            "steps.*.container_id",
            "steps.*.cwl_file",
            "steps.*.stepname",
            "steps.*.tool_status",
            "steps.*.platform.*",
            "steps.*.container.process.*",
        ]
        self.plugins = plugins

        # プラグインで取得したいデータをsourceに追加する
        for plugin in self.plugins:
            self.source.extend(plugin.fetch.get_es_source())

        # ElasticSearch descriptor
        self.es = Elasticsearch([elastic_search_endpoint])

        # Elasticsearch index
        self.index_name = index_name

    # TODO: 関数名にwith_condition をつける?
    def search(self, start_date, end_date, keywords):
        #
        # search workflow list by date, keywords
        #
        query = {}
        wildcards = []
        for cell in self.cells:
            for keyword in keywords:
                if keyword is not None and len(keyword) > 0:
                    wildcards.append(
                        {"wildcard": {cell + ".keyword": "*" + keyword + "*"}}
                    )

        if len(wildcards) > 0:
            query = {"bool": {"should": wildcards}}

        date_ranges = []
        if start_date is not None and start_date != "None" and len(start_date) > 0:
            date_ranges.append(
                {
                    "range": {
                        "workflow.start_date": {
                            "from": "{}T00:00:00.000".format(start_date),
                        }
                    }
                }
            )

        if end_date is not None and end_date != "None" and len(end_date) > 0:
            date_ranges.append(
                {
                    "range": {
                        "workflow.end_date": {"to": "{}T23:59:59.999".format(end_date)}
                    }
                }
            )
        if len(date_ranges) > 0:
            query = {"bool": {"must": date_ranges}}

        # query = {
        #    "bool": {
        #        "should": [
        #            {"wildcard": {"workflow.steps.*.stepname": "*" } },
        #        ]
        #    }
        # }

        # workflow の開始日が最新のものから表示
        sort_param = [{"workflow.start_date": {"order": "desc"}}]
        body = {"_source": self.source, "sort": sort_param}
        if query != {}:
            body = {"query": query, "sort": sort_param, "_source": self.source}

        # post ElasticSearch
        res = self.es.search(index=self.index_name, size=1000, body=body)

        workflows = []
        no = 1
        for hit in res["hits"]["hits"]:
            # add no
            hit["_source"]["no"] = no

            # add workflow_elapsed_sec
            start_date = hit["_source"]["workflow"]["start_date"]
            end_date = hit["_source"]["workflow"]["end_date"]
            hit["_source"]["workflow"][
                "workflow_elapsed_sec"
            ] = dh_util.elapsed_sec(start_date, end_date)

            # step 情報がなければskip
            if "steps" not in hit["_source"] or len(hit["_source"]["steps"]) == 0:
                continue

            # step の start順sort
            sorted_steps = sorted(
                hit["_source"]["steps"].items(), key=lambda x: x[1]["start_date"]
            )
            hit["_source"]["steps"] = dict(sorted_steps)
            workflows.append(hit["_source"])
            no += 1

        return workflows

    # TODO: simpleではなくby_workflow_id か workflowにする?
    def search_simple(self, workflow_id):
        #
        # get workflow by ID
        #
        query = {"match": {"workflow.cwl_file.keyword": workflow_id}}
        body = {"query": query, "_source": self.source}

        # post ElasticSearch
        res = self.es.search(index=self.index_name, body=body)

        if len(res["hits"]["hits"]) == 0:
            return None

        # TODO 確認
        # assert len(res["hits"]["hits"]) == 1

        cwl_workflow_data = res["hits"]["hits"][0]["_source"]
        #
        # elapsed_sec計算
        #
        start_date = cwl_workflow_data["workflow"]["start_date"]
        end_date = cwl_workflow_data["workflow"]["end_date"]
        cwl_workflow_data["workflow"][
            "workflow_elapsed_sec"
        ] = dh_util.elapsed_sec(start_date, end_date)

        #
        # step毎の elapsed_sec 計算
        #
        if "steps" not in cwl_workflow_data:
            # TODO log?
            return None

        is_old_type = False
        for k, v in cwl_workflow_data["steps"].items():
            if "-" not in k:
                # old type workflow format, new is 99-step_name
                is_old_type = True
                break
        if is_old_type:
            return None

        steps_sorted = dict(
            sorted(cwl_workflow_data["steps"].items(), key=lambda x: x[0].split("-")[1])
        )
        cwl_workflow_data["steps"] = steps_sorted

        # stepの実行時間を集計する
        for step_name, val in steps_sorted.items():
            start_date = val["container"]["process"]["start_time"]
            end_date = val["container"]["process"]["end_time"]
            step_elapsed_sec = dh_util.elapsed_sec(start_date, end_date)
            cwl_workflow_data["steps"][step_name]["step_elapsed_sec"] = step_elapsed_sec

        for plugin in self.plugins:
            # TODO: pluginメソッド名見直し
            # TODO; fetchがNoneのときの考慮
            cwl_workflow_data = plugin.fetch.build(cwl_workflow_data)

        # TODO: for each plugin
        # debug code
        # with open("es.json", "w") as f:
        #     f.write(json.dumps(res, indent=2))
        # with open("jsondata.json", "w") as f:
        #     f.write(json.dumps(cwl_workflow_data, indent=2))
        # workflowをidで指定して検索したので、workflowは一つしかないはず
        return cwl_workflow_data
