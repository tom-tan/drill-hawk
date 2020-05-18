# -*- coding: utf-8 -*-
# Copyright 2020 National Institute of Informatics
# SPDX-License-Identifier: Apache-2.0

import re
import copy
import yaml


class Graph:
    def __init__(self, cwl, graph_type):
        # AWS Cost per a hour(ap-northeast-1)
        self.prices_ = []
        with open("prices.yml", "rb") as file:
            prices = yaml.safe_load(file)
            if "prices" not in prices:
                raise ("prices.yaml do not have `prices`")
            self.prices_ = prices["prices"]

        self.cwl_ = cwl
        if graph_type == "elapsed_time":
            self.graph_name = "Elapsed Time"
            self.graph_unit = "sec"
            self.graph_sym = "time"
            other = {"graph_name": "Usage Fee", "graph_type": "usage_fee"}
            self.other = other
        else:
            self.graph_name = "Usage Fee"
            self.graph_unit = "usd"
            self.graph_sym = "cost"
            self.other_type = "elapsed_time"
            other = {"graph_name": "Elapsed Time", "graph_type": "elapsed_time"}
            self.other = other

        self.data = []
        self.total_keys = []
        self.workflows = []

    def get_cost(self, instance_type, workflow_elapsed_sec):

        instance_cost = -1
        for item in self.prices_:
            if item["name"] == instance_type:
                instance_cost = item["price"]

        if instance_cost == -1:
            print(
                "{} instance_cost is not found in aws_prices.yml".format(instance_type)
            )
            raise ("unkown instance_type")

        return workflow_elapsed_sec * instance_cost / 60.0  # 60minutes

    # 指定されたworkflow のstepを抽出
    def build(self, res):

        if "workflow" not in res:
            return None

        wf = res["workflow"]
        d3_workflow = {}  # for d3 data model
        step_no = 10
        steps = []

        for step_name in res["steps"]:
            # remove step_no in step_name-99
            step_name_without_no = re.sub(r"-\d+$", "", step_name)
            step_keys = res["steps"][step_name]
            step_keys["step_name"] = step_name

            instance_type = step_keys["platform"]["ec2_instance_type"]

            d3_workflow["ncpu_cores"] = step_keys["platform"]["ncpu_cores"]
            d3_workflow["total_memory"] = step_keys["platform"]["total_memory"]

            # workflow_id shorting
            # converted_reconf_hisat2-6d6a34a6e1c711e880080210a3f1930c
            # -> converted_reconf_hisat2-6d6a34(6bytes)
            workflow_id = wf["cwl_file"][:-26]
            d3_workflow["workflow_id"] = workflow_id
            d3_workflow["workflow_name"] = workflow_id
            d3_workflow["input_runid"] = wf["inputs"]["filename"]
            d3_workflow["input_size"] = wf["inputs"]["total_size"]
            d3_workflow["workflow_elapsed_sec"] = wf["workflow_elapsed_sec"]
            d3_workflow["prepare_elapsed_sec"] = wf["prepare_elapsed_sec"]
            d3_workflow["total_reconf_elapsed_sec"] = res["total_reconf_elapsed_sec"]

            #
            # d3.js グラフ json data用
            #

            # step 当たりの経過時間
            start_date = step_keys["container"]["process"]["start_time"]
            end_date = step_keys["container"]["process"]["end_time"]
            workflow_elapsed_sec = self.cwl_.workflow_elapsed_sec(start_date, end_date)

            d3_workflow["itype-{}".format(step_name_without_no)] = instance_type
            d3_workflow["time-{}".format(step_name_without_no)] = workflow_elapsed_sec
            # cost(fee/hour) * cost time(sec)
            d3_workflow["cost-{}".format(step_name_without_no)] = self.get_cost(
                instance_type, workflow_elapsed_sec
            )

            d3_workflow["id-{}".format(step_name_without_no)] = step_keys["container"][
                "process"
            ]["id"]
            d3_workflow["start-{}".format(step_name_without_no)] = start_date
            d3_workflow["end-{}".format(step_name_without_no)] = end_date

            # グラフ出力する項目名の設定
            key_name = "{}-{}".format(self.graph_sym, step_name_without_no)

            if key_name not in self.total_keys:
                # keyは複数のworkflowのstep名のuniqリスト
                # 00-tool_id
                self.total_keys.append("{:02d}-{}".format(step_no, key_name))
            step_no += 1

            # 表用
            steps.append(step_keys)

        #
        # reconf合計 stepを追加する
        #
        name = "_total_reconf"
        d3_workflow["id-{}".format(name)] = "{}-01".format(name)
        d3_workflow["time-{}".format(name)] = res["total_reconf_elapsed_sec"]
        d3_workflow["cost-{}".format(name)] = 0
        d3_workflow["start-{}".format(name)] = ""
        d3_workflow["end-{}".format(name)] = ""
        # グラフ出力する項目名の設定
        self.total_keys.insert(0, "{:02d}-{}-{}".format(2, self.graph_sym, name))
        steps.insert(0, self.null_metrics(name))

        #
        # prepare stepを追加する
        #
        name = "_prepare"
        d3_workflow["id-{}".format(name)] = "{}-01".format(name)
        d3_workflow["time-{}".format(name)] = wf["prepare_elapsed_sec"]
        d3_workflow["cost-{}".format(name)] = 0
        d3_workflow["start-{}".format(name)] = ""
        d3_workflow["end-{}".format(name)] = ""
        self.total_keys.insert(0, "{:02d}-{}-{}".format(1, self.graph_sym, name))
        steps.insert(0, self.null_metrics(name))

        #
        # グラフデータのモデル最終構築
        #
        self.data.append(d3_workflow)
        workflow_tbl = copy.copy(d3_workflow)
        workflow_tbl["steps"] = steps

        # d3.js は データの順番が逆になるので、表も逆にしておく
        self.workflows.insert(0, workflow_tbl)

        for workflow in self.data:
            # 異なるworkflow の場合、足りないstepを埋めておく
            for keyname in self.total_keys:
                if keyname not in workflow:
                    workflow[keyname] = 0

        return

    def null_metrics(self, stepname):
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
