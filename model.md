# graph用 Javascript記述

## グラフ定義

`initStackedBarChart.draw()` 関数に、描画するグラフの基本データを引き渡す
引数は、以下の通り。

- data ... json データ
- key ... グラフ表示するkey名定義
- unit_string ... 単位
- element ... d3のグラフタイプ名

key名は、 `{cost|time}-workflowのstep名` とする。
`cost` は料金、 `time` はかかった時間を意味する。
例えば、cufflinks は、 `cost-cufflinks` 。

なお、reconf用には、以下の特別なkey名を利用する。

- {cost|time}-_prepare
- {cost|time}-_total_reconf


```
  var usage_fee_key =
  ['cost-_prepare', 'cost-_total_reconf', 'cost-HISAT2', 'cost-cufflinks']
  ;
  initStackedBarChart.draw({
    data: data,
    key: usage_fee_key,
    unit_string: 'usd',
    element: 'gantt-bar'
  });
```

## d3 用データ

### 基本的な構造

```
[
    { workflow1 },
    { workflow2 }
]
```

workflow は、以下の通り

```
{
    workflow 全体情報,
    "00-key名": 0,                              # 表示順は、 `00` 部で決まる
    ...
    "cost-HISAT2": 24.4388,                     # 各stepのcost
    "time-HISAT2": 1713,                        # 各stepのtime
    "start-HISAT2": "2020-05-05T14:25:01",      # 各stepの開始時間
    "end-HISAT2": "2020-05-05T14:53:34",        # 各stepの終了時間
    "itype-HISAT2": "c5.4xlarge",               # 各stepのinstance type
    "id-HISAT2": "71b3329e80f6b08665e709aa6fc282556e307e17a72cf38578d2c1aa78db97bc",
                                                # 各stepのcontainer_id
    ... 
}
```

workflow 全体情報は、以下の通り

| 項目名 | 説明 | sample |
|-----|----------------|---------|
| workflow_id | workflow id | reconf_hisat2_cufflinks-d04a47" |
| workflow_name | workflow name | reconf_hisat2_cufflinks-d04a47" |
| input_runid | workflow のinput file | http://localhost:8000/ERR188384_1.fastq" |
| input_size | input file size | 10909719910 |
| ncpu_cores |  要求CPU数? | 16 |
| total_memory | 要求メモリ数? | 32662736896 | 
| workflow_elapsed_sec | workflow 全体にかかった時間 |2655 |
| prepare_elapsed_sec | prepare 処理にかかった時間 | 7 |
| total_reconf_elapsed_sec | reconf のかかった合計時間 | 222 |


### サンプル

```
[
    {
        "total_memory": 32662736896,
        "total_reconf_elapsed_sec": 222,
        "workflow_elapsed_sec": 2655,
        "workflow_id": "reconf_hisat2_cufflinks-d04a47",
        "workflow_name": "reconf_hisat2_cufflinks-d04a47"
        "input_runid": "http://localhost:8000/ERR188384_1.fastq",
        "input_size": 10909719910,
        "ncpu_cores": 16,
        "prepare_elapsed_sec": 7,

        "01-time-_prepare": 0,
        "02-time-_total_reconf": 0,
        "10-time-HISAT2": 0,
        "11-time-cufflinks": 0,

        "cost-HISAT2": 24.4388,
        "cost-_prepare": 0,
        "cost-_total_reconf": 0,
        "cost-cufflinks": 5.3642666666666665,

        "time-HISAT2": 1713,
        "time-_prepare": 7,
        "time-_total_reconf": 222,
        "time-cufflinks": 376,

        "start-HISAT2": "2020-05-05T14:25:01",
        "start-_prepare": "",
        "start-_total_reconf": "",
        "start-cufflinks": "2020-05-05T14:56:30",

        "end-HISAT2": "2020-05-05T14:53:34",
        "end-_prepare": "",
        "end-_total_reconf": "",
        "end-cufflinks": "2020-05-05T15:02:46",
        
        "itype-HISAT2": "c5.4xlarge",
        "itype-cufflinks": "c5.4xlarge",
        
        "id-HISAT2": "71b3329e80f6b08665e709aa6fc282556e307e17a72cf38578d2c1aa78db97bc",
        "id-_prepare": "_prepare-01",
        "id-_total_reconf": "_total_reconf-01",
        "id-cufflinks": "cb9356e7f7a5c8678ce0e5e85c4759a8fa6b9ba04556aec3f423da56de37bd41",
    }
]
```

## 表用データ(flask template)

### 基本的な構造

```
[
    { workflow1 },
    { workflow2 }
]
```

workflow は、以下の通り

```
{
    workflow 全体情報,
    "steps": [ 
        { prepare 情報 },
        { reconf 情報 },
        { step 情報 },                          # workflow(ElasticSearch)のstepと同じ
        ...
    ]                              

...
    "cost-HISAT2": 24.4388,                     # 各stepのcost
    "time-HISAT2": 1713,                        # 各stepのtime
    "start-HISAT2": "2020-05-05T14:25:01",      # 各stepの開始時間
    "end-HISAT2": "2020-05-05T14:53:34",        # 各stepの終了時間
    "itype-HISAT2": "c5.4xlarge",               # 各stepのinstance type
    "id-HISAT2": "71b3329e80f6b08665e709aa6fc282556e307e17a72cf38578d2c1aa78db97bc",
                                                # 各stepのcontainer_id
    ... 
}
```

### sample

```
[
  {
    "ncpu_cores": 16,
    "total_memory": 32662736896,
    "workflow_id": "reconf_hisat2_cufflinks-d04a47",
    "workflow_name": "reconf_hisat2_cufflinks-d04a47",
    "input_runid": "http://localhost:8000/ERR188384_1.fastq",
    "input_size": 10909719910,
    "workflow_elapsed_sec": 2655,
    "prepare_elapsed_sec": 7,
    "total_reconf_elapsed_sec": 222,

    "itype-HISAT2": "c5.4xlarge",
    "time-HISAT2": 1713,
    "cost-HISAT2": 24.4388,
    "id-HISAT2": "71b3329e80f6b08665e709aa6fc282556e307e17a72cf38578d2c1aa78db97bc",
    "start-HISAT2": "2020-05-05T14:25:01",
    "end-HISAT2": "2020-05-05T14:53:34",

    "itype-cufflinks": "c5.4xlarge",
    "time-cufflinks": 376,
    "cost-cufflinks": 5.3642666666666665,
    "id-cufflinks": "cb9356e7f7a5c8678ce0e5e85c4759a8fa6b9ba04556aec3f423da56de37bd41",
    "start-cufflinks": "2020-05-05T14:56:30",
    "end-cufflinks": "2020-05-05T15:02:46",
    
    "id-_total_reconf": "_total_reconf-01",
    "time-_total_reconf": 222,
    "cost-_total_reconf": 0,
    "start-_total_reconf": "",
    "end-_total_reconf": "",

    "id-_prepare": "_prepare-01",
    "time-_prepare": 7,
    "cost-_prepare": 0,
    "start-_prepare": "",
    "end-_prepare": "",

    "steps": [
      {
        "start_date": "",
        "end_date": "",
        "container": {
          "process": {
            "image": "",
            "start_time": "",
            "end_time": "",
            "exit_code": 0,
            "id": "_prepare",
            "cmd": None,
            "status": None
          }
        },
        "stepname": "_prepare",
        "step_name": "_prepare",
        "tool_status": "ok",
        "cwl_file": "_prepare",
        "platform": {
          "hostname": "",
          "total_memory": 0,
          "ec2_instance_type": "",
          "disk_size": None,
          "ncpu_cores": 0,
          "ec2_ami_id": None,
          "ec2_region": ""
        }
      },
      {
        "start_date": "",
        "end_date": "",
        "container": {
          "process": {
            "image": "",
            "start_time": "",
            "end_time": "",
            "exit_code": 0,
            "id": "_total_reconf",
            "cmd": None,
            "status": None
          }
        },
        "stepname": "_total_reconf",
        "step_name": "_total_reconf",
        "tool_status": "ok",
        "cwl_file": "_total_reconf",
        "platform": {
          "hostname": "",
          "total_memory": 0,
          "ec2_instance_type": "",
          "disk_size": None,
          "ncpu_cores": 0,
          "ec2_ami_id": None,
          "ec2_region": ""
        }
      },
      {
        "end_date": "2020-05-05T14:54:06",
        "container": {
          "process": {
            "image": "limesbonn/hisat2",
            "start_time": "2020-05-05T14:25:01",
            "end_time": "2020-05-05T14:53:34",
            "exit_code": 0,
            "id": "71b3329e80f6b08665e709aa6fc282556e307e17a72cf38578d2c1aa78db97bc",
            "cmd": None,
            "status": None
          }
        },
        "reconf": {
          "start_time": "2020-05-05T14:22:23",
          "end_time": "2020-05-05T14:24:36",
          "ra": {
            "start_time": "2020-05-05T14:22:23.409770",
            "end_time": "2020-05-05T14:24:29.092136"
          }
        },
        "stepname": "HISAT2-3",
        "tool_status": "ok",
        "cwl_file": "HISAT2-3",
        "platform": {
          "hostname": "ip-172-30-2-213",
          "total_memory": 32662736896,
          "ec2_instance_type": "c5.4xlarge",
          "disk_size": None,
          "ncpu_cores": 16,
          "ec2_ami_id": None,
          "ec2_region": "ap-northeast-2"
        },
        "start_date": "2020-05-05T14:24:37",
        "step_elapsed_sec": 1713,
        "reconf_elapsed_sec": 126,
        "as_elapsed_sec": 0,
        "ra_elapsed_sec": 126,
        "step_name": "HISAT2-3"
      },
      {
        "end_date": "2020-05-05T15:02:49",
        "container": {
          "process": {
            "image": "nasuno/cufflinks",
            "start_time": "2020-05-05T14:56:30",
            "end_time": "2020-05-05T15:02:46",
            "exit_code": 0,
            "id": "cb9356e7f7a5c8678ce0e5e85c4759a8fa6b9ba04556aec3f423da56de37bd41",
            "cmd": None,
            "status": None
          }
        },
        "reconf": {
          "start_time": "2020-05-05T14:54:07",
          "end_time": "2020-05-05T14:55:51",
          "ra": {
            "start_time": "2020-05-05T14:54:08.101633",
            "end_time": "2020-05-05T14:55:43.728662"
          }
        },
        "stepname": "cufflinks-5",
        "tool_status": "ok",
        "cwl_file": "cufflinks-5",
        "platform": {
          "hostname": "ip-172-30-2-123",
          "total_memory": 32662736896,
          "ec2_instance_type": "c5.4xlarge",
          "disk_size": None,
          "ncpu_cores": 16,
          "ec2_ami_id": None,
          "ec2_region": "ap-northeast-2"
        },
        "start_date": "2020-05-05T14:55:54",
        "step_elapsed_sec": 376,
        "reconf_elapsed_sec": 96,
        "as_elapsed_sec": 1,
        "ra_elapsed_sec": 95,
        "step_name": "cufflinks-5"
      }
    ]
  }
]
```
