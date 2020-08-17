FROM python:3.7-alpine

ARG project_dir=/app/

COPY requirements.txt /tmp

WORKDIR $project_dir

RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN apk --no-cache add gettext=~0.20.2

CMD ["python", "app.py"]
