# build zeroc-ice wheel in first stage
# this is a fat container becouse of the required dependencies
# to compile the package — it will also take a couple minutes to finish
FROM python:3.10 AS zeroc-ice

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
	libbz2-dev software-properties-common build-essential libssl-dev 
ENV ICE_VERSION="3.6.5"
RUN pip install --upgrade pip && \
	pip install wheel && \
	pip download "zeroc-ice==$ICE_VERSION"
RUN tar -zxf "zeroc-ice-$ICE_VERSION.tar.gz" && \
	cd "zeroc-ice-$ICE_VERSION" && \
	python setup.py bdist_wheel

# build omero-py container in second stage
# this keeps the whole build lighter
FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]

ENV PYTHONNOUSERSITE=1
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y git

# copy over zeroc_ice.whl from the first stage
ENV ZEROC_ICE_WHL=zeroc_ice-3.6.5-cp310-cp310-linux_x86_64.whl
COPY --from=zeroc-ice /zeroc-ice-3.6.5/dist/${ZEROC_ICE_WHL} ./

# create venv and install zeroc-ice and then omero-py
RUN python3 -m venv /env && \
    pip install --upgrade pip --no-cache-dir && \
    pip install ${ZEROC_ICE_WHL} --no-cache-dir && \
    pip install omero-py --no-cache-dir
RUN pip install git+https://github.com/cellgeni/omero-download.git

# cleanup
RUN rm -rf ${ZEROC_ICE_WHL}


COPY Dockerfile /docker/
RUN chmod -R 755 /docker

