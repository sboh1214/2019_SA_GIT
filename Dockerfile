FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir Test
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY /Test /Test