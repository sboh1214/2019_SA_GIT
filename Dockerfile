FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir Test
WORKDIR /Test
COPY requirements.txt /Test
RUN pip install -r requirements.txt
COPY /Test /Test