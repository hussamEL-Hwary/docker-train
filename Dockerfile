FROM python:2.7
LABEL maintainer "Hwary <hossam.elhwary1996@gmail.com>"
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_ENV="docker"
EXPOSE 5000
