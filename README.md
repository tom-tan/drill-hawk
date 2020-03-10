# DrillHawk

It is a web application to visualize previous workflow execution records collected by [CWL-metrics](https://inutano.github.io/cwl-metrics/).
It enables us to take a [drill down](https://en.wikipedia.org/wiki/Drill_down) approach in which we first check the list of collected workflow execution records, compare several execution records using workflow metrics, and analyze the specific execution records by using [Kibana](https://www.elastic.co/kibana).

# Requirements

- Python 3.7
- Elasticsearch that stores workflow metrics collected by CWL-metrics or its compatible metrics collector
- Kibana
  - [Setup](doc/manual.md) is needed to drill down from DrillHawk

# How to start DrillHawk server
```console
$ git clone https://bitbucket.org/dynreconf/drill-hawk.git
$ cd drill-hawk
$ pip install -r requirements.txt
$ export ES_INDEX_NAME=workflow
$ export ES_ENDPOINT=10.0.0.100:9200
$ export KIBANA_ENDPOINT=10.0.0.100:5601
$ python app.py
```

You can see the list of collected workflow execution records at `http://localhost:5001/`.
You can configure the index name and the endpoint of Elasticsearch by using `ES_INDEX_NAME` and `ES_ENDPOINT`, `KIBANA_ENDPOINT` respectively.

# Starting DrillHawk server using docker-compose
If you prefer using docker containers, you can start DrillHawk server by using the following command:

```console
$ docker-compose up
```
