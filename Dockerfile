FROM python:3.9-alpine3.13
LABEL maintainer="londonappdeveloper.com"
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000
# defines a build argument called dev and sets the default value to false. Override this in docker compose file by specifyng args dev=true.
ARG DEV=false    
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    #shell script: if dev env variable w/c is a build arg set to true then run code.
    if [ $DEV="true"]; \  
    #if dev=true, it will install dev dependencies. When we run dockerfile with dev =true, it will install actual
    #dependencies with requirements.txt and also the dev dependencies. However ifwe build w/o dev being true, dev
    #dependencies won't be installled on docker image adding security and saving space bcz no worries about bugs
    #things in development dependencies if we don't install them on production image.
        then /py/bin/pip install -r /tmp/requirementd.dev.txt; \
    fi && \ 
    #this is how we end if stmt. in shell script. This is how we run shell command conditionally.
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"
USER django-user