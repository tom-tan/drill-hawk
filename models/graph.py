# -*- coding: utf-8 -*-
# Copyright 2020 National Institute of Informatics
# SPDX-License-Identifier: Apache-2.0

import re
import copy
import yaml


class Graph:
    def __init__(self, cwl, graph_type, plugins):
        """

        Attributes:
          data        d3_workflow のデータ部分(逆順)
          total_keys  グラフ種別とステップ名(番号を除いたもの)の接頭辞として番号をつけたリスト
          workflows   表のデータ。d3_workflow にstepsを追加したもの(逆順)
        """

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
        # table描画用のデータ
        self.workflows = []
        self.plugins = plugins

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
    # TODO resをworkflow_dataにリネーム
    def build(self, workflow_data):
        """
        """
        print("graph build")
        if "workflow" not in workflow_data:
            return None

        wf = workflow_data["workflow"]
        d3_workflow = {}  # for d3 data model
        step_no = 10
        steps = []

        for step_name in workflow_data["steps"]:
            # remove step_no in step_name-99
            step_name_without_no = re.sub(r"-\d+$", "", step_name)
            step_keys = workflow_data["steps"][step_name]
            # TODO: 確認 データ上stepnameになっているが
            step_keys["step_name"] = step_name

            instance_type = step_keys["platform"]["ec2_instance_type"]

            # TODO: stepごとにd3_workflow上のキーを分ける必要が有るのでは?
            d3_workflow["ncpu_cores"] = step_keys["platform"]["ncpu_cores"]
            d3_workflow["total_memory"] = step_keys["platform"]["total_memory"]

            # TODO: stepに無関係(stepが有る場合に実行したい?)
            # TOOD: step_nameのループの外に出す?
            # workflow_id shorting
            # converted_reconf_hisat2-6d6a34a6e1c711e880080210a3f1930c
            # -> converted_reconf_hisat2-6d6a34(6bytes)
            # TODO: workflow_id が十分長いときだけ切る (reconf以外のcwl_fileの場合の対応)
            workflow_id = wf["cwl_file"][:-26]
            d3_workflow["workflow_id"] = workflow_id
            d3_workflow["workflow_name"] = workflow_id
            d3_workflow["input_runid"] = wf["inputs"]["filename"]
            d3_workflow["input_size"] = wf["inputs"]["total_size"]
            d3_workflow["workflow_elapsed_sec"] = wf["workflow_elapsed_sec"]
            # TODO: ここまで　stepに無関係(stepが有る場合に実行したい?)

            #
            # d3.js グラフ json data用
            #

            # step 当たりの経過時間
            start_date = step_keys["container"]["process"]["start_time"]
            end_date = step_keys["container"]["process"]["end_time"]
            # TODO: utilで定義するか、引き算して時間を出す(cwlの引き渡しをやめる)
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

            # key_name graph_sym, step_name
            # TODO: cost, timeを同じにする?
            for graph_sym in ["time", "cost"]:
                key_name = "{}-{}".format(graph_sym, step_name_without_no)

                if key_name not in self.total_keys:
                    # keyは複数のworkflowのstep名のuniqリスト
                    # 00-tool_id
                    self.total_keys.append("{:02d}-{}".format(step_no, key_name))
            step_no += 1

            # 表用
            steps.append(step_keys)

        # self.total_keys
        total_keys = self.total_keys
        for plugin in self.plugins:
            (d3_workflow, step, total_keys) = plugin.graph.build(
                self.graph_sym, workflow_data, d3_workflow, steps, total_keys
            )
            print("after d3_workflow {}".format(d3_workflow))

        workflow_tbl = copy.copy(d3_workflow)
        workflow_tbl["steps"] = steps
        self.total_keys = total_keys
        #
        # グラフデータのモデル最終構築
        #
        self.data.append(d3_workflow)
        # d3.js は データの順番が逆になるので、表も逆にしておく
        self.workflows.insert(0, workflow_tbl)

        for workflow in self.data:
            # 異なるworkflow の場合、足りないstepを埋めておく
            for keyname in self.total_keys:
                if keyname not in workflow:
                    workflow[keyname] = 0

        return
