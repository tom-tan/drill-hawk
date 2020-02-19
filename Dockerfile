FROM python:3.7

ARG project_dir=/app/

ADD requirements.txt /tmp

WORKDIR $project_dir

RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD ["python", "app.py"]
