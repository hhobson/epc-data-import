FROM python:3.7.4-slim
LABEL maintainer="hhobson"

RUN apt-get update && \
    # Install dependencies
    apt-get install -y --no-install-recommends \
    curl \
    unzip && \
    apt-get autoremove -y --purge && \
    apt-get clean

# ENV PATH=~/.local/bin:$PATH

COPY requirements.txt /dependencies/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r dependencies/requirements.txt

WORKDIR /usr/local
COPY src /usr/local/bin

CMD ["/bin/bash"]