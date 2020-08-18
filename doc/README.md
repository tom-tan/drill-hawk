# How to build DrillHawk plugin API documentation

## Requirements

* docker-compose
* docker

## Build

1. Build container image of DrillHawk, which will be named `drill-hawk_web`

```
( cd ..; docker-compose build )
```

2. Build container image of document builder. Execute following command in 
doc` directory.

```
docker-compose build
```

## Generate Document

```
./build.sh
```

Generated document is  `_build/singlehtml/index.html` .
