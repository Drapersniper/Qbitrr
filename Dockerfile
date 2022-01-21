# Pin Python to the latest supported version (This avoid it auto updating to a higher untested version)
FROM python:3.10

LABEL Maintainer="Draper"

# Env used by the script to determine if its inside a docker - if this is set to 69420 it will change the working dir for docker specific values
ENV QBITRR_DOCKER_RUNNING=69420

COPY . /app

RUN python -m pip install -r /app/requirements.extras.txt -r /app/requirements.txt && python /app/setup.py install

ENTRYPOINT ["python", "-m", "qBitrr.main"]
