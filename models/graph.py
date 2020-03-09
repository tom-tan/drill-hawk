# -*- coding: utf-8 -*-
# Copyright 2020 National Institute of Informatics
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
import re
import copy


class Graph:
    def __init__(self, cwl, graph_type):
        # AWS Cost per a hour(ap-northeast-1)
        self.costs_ = {
            "t2.medium": 0.0608,
            "t3.large": 0.1088,
            "c5.2xlarge": 0.428,
            "c5.4xlarge": 0.856,
            "m5.2xlarge": 0.496,
            "m5.4xlarge": 0.992,
            "r5.large": 0.152,
            "r5.2xlarge": 0.608,
            "r5.4xlarge": 1.216,
        }

        self.cwl_ = cwl
        if graph_type == "elapsed_time":
            self.graph_name = "Elapsed Time"
            self.graph_unit = "sec"
            self.graph_sym = "time"
            other = {"graph_name": "UserFee", "graph_type": "usage_fee"}
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
            step_name_without_no = re.sub("-\d+$", "", step_name)
            step_keys = res["steps"][step_name]
            step_keys["step_name"] = step_name

            instance_type = step_keys["platform"]["ec2_instance_type"]

            d3_workflow["ncpu_cores"] = step_keys["platform"]["ncpu_cores"]
            d3_workflow["total_memory"] = step_keys["platform"]["total_memory"]

            # workflow_id shorting
            workflow_id = wf["cwl_file"][:-26]
            d3_workflow["workflow_id"] = workflow_id
            d3_workflow["workflow_name"] = workflow_id
            d3_workflow["input_runid"] = wf["inputs"]["filename"]
            d3_workflow["input_size"] = wf["inputs"]["total_size"]
            d3_workflow["workflow_elapsed_sec"] = wf["workflow_elapsed_sec"]

            #
            # d3.js グラフ json data用
            #

            # step 当たりの経過時間
            start_date = step_keys["start_date"]
            end_date = step_keys["end_date"]
            workflow_elapsed_sec = self.cwl_.workflow_elapsed_sec(start_date, end_date)

            d3_workflow["itype-{}".format(step_name_without_no)] = instance_type
            d3_workflow["time-{}".format(step_name_without_no)] = workflow_elapsed_sec
            # cost(fee/hour) * cost time(sec)
            d3_workflow["cost-{}".format(step_name_without_no)] = (
                workflow_elapsed_sec * self.costs_[instance_type] / 60.0
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
