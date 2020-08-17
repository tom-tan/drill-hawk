# FROM python:3.7-alpine
FROM drill-hawk_web

## 共通
RUN apk add --update make git py3-sphinx make
RUN pip3 install sphinx_rtd_theme

# 日本語対応
RUN update-locale LANG=ja_JP.UTF-8
ENV LC_CTYPE C.UTF-8

RUN curl -LO https://github.com/jgm/pandoc/releases/download/2.5/pandoc-2.5-1-amd64.deb
RUN dpkg -i pandoc-2.5-1-amd64.deb && rm pandoc-2.5-1-amd64.deb

# COPY filter.patch columns.patch ./
# RUN patch -d/ -p0 < filter.patch
# RUN patch -d/ -p0 < columns.patch

WORKDIR /app/
