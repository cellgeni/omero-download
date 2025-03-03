FROM python:3.11
COPY . /opt/omero-download
RUN pip install /opt/omero-download
