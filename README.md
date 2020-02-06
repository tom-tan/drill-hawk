# DrillHawk

It is a visualizer of previous workflow execution records collected by [CWL-metrics](https://inutano.github.io/cwl-metrics/).
It enables us to take a [drill down](https://en.wikipedia.org/wiki/Drill_down) approach in which we first check the list of collected workflow execution records, compare several execution records using workflow metrics, and analyze the specific execution records by using [Kibana](https://www.elastic.co/kibana).

# Requirements

- Python 3.6 or later
- Elasticsearch that stores workflow metrics using CWL-metrics or its compatible metrics collector
- Kibana
  - [Setup](doc/manual.md) is needed to drill down from DrillHawk

## Install
```console
$ git clone https://bitbucket.org/dynreconf/drill-hawk.git
$ cd drill-hawk
$ pip install -r requirements.txt
```

# How to use
```console
$ export ES_INDEX_NAME=workflow
$ export ES_ENDPOINT=$ELASTIC_SEARCH_IP:9200
$ python app.py
```

You can see the list of collected workflow execution records in DrillHawk at `http://localhost:5001/`.
You can configure the index name and endpoint of elasticsearch by using `ES_INDEX_NAME` and `ES_ENDPOINT`, respectively.


# Setup using docker-compose
If you prefer using docker container, you can setup DrillHawk by using the following command:

```console
$ docker-compose up
```
