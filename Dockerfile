FROM python:3.10

RUN apt-get update && apt-get  install -y \
        gdal-bin \
        libgdal-dev \
        python3-gdal

WORKDIR /code

RUN pip install GDAL==3.4.1

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN pip install git+https://github.com/TaskarCenterAtUW/TDEI-python-ms-core@feature-testing-from-branch

COPY ./src /code/src
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
