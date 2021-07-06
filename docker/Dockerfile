FROM ubuntu:20.04
MAINTAINER Christian Klinger <cklinger@novareto.de>

# First we configure the TZ, or it will hang on the update
ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# We update it all
RUN apt-get -y update && apt-get install -y curl wget gnupg2 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install RabbitMQ
RUN curl -OL https://dl.bintray.com/rabbitmq/Keys/rabbitmq-release-signing-key.asc && apt-key add - < rabbitmq-release-signing-key.asc && \
    curl -OL https://www.rabbitmq.com/rabbitmq-release-signing-key.asc && apt-key add - < rabbitmq-release-signing-key.asc && \
    echo "deb https://dl.bintray.com/rabbitmq-erlang/debian focal erlang-22.x" | tee /etc/apt/sources.list.d/rabbitmq.list && \
    apt-get -y update && apt-get -y install rabbitmq-server

# Install python3.8
RUN apt-get update && apt install -y curl python3-pip python3-dev ssh && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Arango
RUN echo arangodb3 arangodb3/password password admin | debconf-set-selections && \
    echo arangodb3 arangodb3/password_again password admin | debconf-set-selections && \
    echo arangodb3 arangodb3/upgrade boolean true | debconf-set-selections && \
    echo arangodb3 arangodb3/storage_engine select rocksdb | debconf-set-selections && \
    echo arangodb3 arangodb3/backup boolean true | debconf-set-selections

RUN curl -OL https://download.arangodb.com/arangodb37/DEBIAN/Release.key && apt-key add - < Release.key && \
    echo 'deb https://download.arangodb.com/arangodb37/DEBIAN/ /' | tee /etc/apt/sources.list.d/arangodb.list && \
    apt-get install apt-transport-https && \
    apt-get update && \
    apt-get install -y arangodb3=3.7.10-1

#  Install git
RUN apt-get install --assume-yes git python3-pip

# Clone project
ENV PROJECT_NAME uvcreha
ENV ENV_NAME uvcreha
ENV PIP=21.0.1 \
    ZC_BUILDOUT=3.0a2 \
    SETUPTOOLS=51.1.0 \
    WHEEL=0.36.2
RUN pip3 install pip==$PIP setuptools==$SETUPTOOLS zc.buildout==$ZC_BUILDOUT wheel==$WHEEL cookiecutter
RUN cookiecutter https://github.com/novareto/uvc_reha_project 
RUN cd /portal \
&& buildout
