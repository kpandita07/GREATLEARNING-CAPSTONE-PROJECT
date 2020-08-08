FROM ubuntu:latest
RUN echo Updating existing packages, installing and upgrading python and pip.
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN python3 -m pip install --upgrade pip
RUN echo Copying the Safety Essentials Flask service into a service directory.
COPY ./service /SafetyEssentialsService
WORKDIR /SafetyEssentialsService
RUN echo Installing Python packages listed in requirements.txt
RUN python3 -m pip install -r ./requirements.txt
RUN echo Starting python and starting the Flask service...
ENTRYPOINT ["python3"]
CMD ["safetyEssentialsService.py"]
