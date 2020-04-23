# -*- coding: utf-8 -*-
# Copyright 2020 National Institute of Informatics
# SPDX-License-Identifier: Apache-2.0

from elasticsearch import Elasticsearch
from datetime import datetime


class CwlMetrics:
    def __init__(self, elastic_search_endpoint, index_name, cells=None):

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

        # ElasticSearch discrptor
        self.es = Elasticsearch([elastic_search_endpoint])

        # Elasticsearch index
        self.index_name = index_name

    def search(self, start_date, end_date, keywords):
        #
        # get workflow
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
            ] = self.workflow_elapsed_sec(start_date, end_date)

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

    def search_simple(self, workflow_id):
        #
        # get workflow
        #
        query = {"match": {"workflow.cwl_file.keyword": workflow_id}}
        body = {"query": query, "_source": self.source}

        # post ElasticSearch
        res = self.es.search(index=self.index_name, body=body)

        workflows = []
        for hit in res["hits"]["hits"]:

            #
            # workflow_elapsed_sec計算
            #
            start_date = hit["_source"]["workflow"]["start_date"]
            end_date = hit["_source"]["workflow"]["end_date"]
            hit["_source"]["workflow"][
                "workflow_elapsed_sec"
            ] = self.workflow_elapsed_sec(start_date, end_date)

            #
            # step毎の elapsed_sec 計算
            #
            if "steps" not in hit["_source"]:
                continue

            is_old_type = False
            for k, v in hit["_source"]["steps"].items():
                if "-" not in k:
                    # old type workflow format, new is 99-step_name
                    is_old_type = True
                    break
            if is_old_type:
                continue

            steps_sorted = dict(
                sorted(
                    hit["_source"]["steps"].items(), key=lambda x: x[0].split("-")[1]
                )
            )
            hit["_source"]["steps"] = steps_sorted
            for step_name, val in steps_sorted.items():
                start_date = val["container"]["process"]["start_time"]
                end_date = val["container"]["process"]["end_time"]
                step_elapsed_sec = self.workflow_elapsed_sec(start_date, end_date)
                hit["_source"]["steps"][step_name][
                    "step_elapsed_sec"
                ] = step_elapsed_sec

            # 完成したworkflow 保存
            workflows.append(hit["_source"])

        if len(workflows) == 0:
            return None
        else:
            return workflows[0]

    def workflow_elapsed_sec(self, start_date, end_date):
        """
        end_data - start_date の秒数計算
        """
        start_timestamp = datetime.strptime(start_date[0:19], "%Y-%m-%dT%H:%M:%S")
        end_timestamp = datetime.strptime(end_date[0:19], "%Y-%m-%dT%H:%M:%S")
        workflow_elapsed_sec = (end_timestamp - start_timestamp).total_seconds()

        return int(workflow_elapsed_sec)

    def sort_step(self, steps):
        """
        stepのdictをstart_date順にsortする
        """
        return steps
