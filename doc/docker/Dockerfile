# FROM python:3.7-alpine
# DrillHawkをdocker-composeでビルドしたイメージ `drill-hawk_web` をベースにする
FROM drill-hawk_web

## 共通
RUN apk add --update make git py3-sphinx make curl patch
RUN pip3 install sphinx_rtd_theme sphinxcontrib-pandoc-markdown
#sphinxcontrib-pandoc-markdown

# 日本語対応
# RUN update-locale LANG=ja_JP.UTF-8
ENV LC_CTYPE C.UTF-8

# markdown対応は保留
# RUN curl -LO https://github.com/jgm/pandoc/releases/download/2.5/pandoc-2.5-1-amd64.deb
#RUN dpkg -i pandoc-2.5-1-amd64.deb && rm pandoc-2.5-1-amd64.deb
RUN curl -LO https://github.com/jgm/pandoc/releases/download/2.10.1/pandoc-2.10.1-linux-amd64.tar.gz \
&& tar xvzf pandoc-2.10.1-linux-amd64.tar.gz --strip-components 1 -C /usr/local/ \
&& rm -rf pandoc-2.10.1-linux-amd64.tar.gz

COPY filter.patch columns.patch ./
#RUN patch -d/ -p0 < filter.patch
#RUN patch -d/ -p0 < columns.patch

CMD ["make", "singlehtml"]
WORKDIR /app/doc
