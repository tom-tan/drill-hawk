FROM python:3.7

ARG project_dir=/app/

COPY requirements.txt /tmp

WORKDIR $project_dir

RUN apt-get update -y
RUN apt-get install -y  gettext libxml2-dev libxslt-dev gcc bash graphviz
# RUN apt-get install -y  gettext libxml2-dev libxslt-dev gcc bash libc-dev linux-headers graphvizk
RUN pip install --no-cache-dir -r /tmp/requirements.txt


CMD ["python", "app.py"]
