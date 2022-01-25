# Pin Python to the latest supported version
# (This avoid it auto updating to a higher untested version)
FROM python:3.10

LABEL Maintainer="Draper"

# Env used by the script to determine if its inside a docker -
# if this is set to 69420 it will change the working dir for docker specific values
ENV QBITRR_DOCKER_RUNNING=69420

COPY . /app

WORKDIR /app/

RUN python -m pip install -e .[ujson]

WORKDIR /config

ENTRYPOINT ["python", "-m", "qBitrr.main"]
