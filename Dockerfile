FROM python:2-alpine

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
  && pip install -r /tmp/requirements.txt

COPY . /app

ENV PORT 7000
EXPOSE 7000
CMD ["python", "email_pre_processing_service.py"]
