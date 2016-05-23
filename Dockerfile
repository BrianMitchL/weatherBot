FROM python:3
MAINTAINER Brian Mitchell <bman4789@gmail.com>

COPY . /src
WORKDIR /src
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "weatherBot.py", "weatherBot.conf"]
