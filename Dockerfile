FROM python:3.11 AS compile-image

# Create a virtual environment in which we install the Python packages described in the requirements file.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install the "curl" and "jq" packages, needed for the Quarto tool.
RUN apt-get update && apt-get install -yq --no-install-recommends \
    curl \
    jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install the Quarto tool.
RUN QUARTO_VERSION=$(curl https://api.github.com/repos/quarto-dev/quarto-cli/releases/latest | jq '.tag_name' | sed -e 's/[\"v]//g') && \
    wget https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz && \
    tar -xvzf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz && \
    ln -s quarto-${QUARTO_VERSION} quarto-dist && \
    rm -rf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz

# Use a lightweight version of Python 3.11 in the final Docker image.
FROM python:3.11-slim AS runner-image

#  Install the "curl" package.
RUN apt-get update && apt-get install -yq --no-install-recommends \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Creates a user and group for running the Quarto tool.
RUN groupadd -g 1069 python && \
    useradd -r -u 1069 -g python python

# Set the working directory for the Docker image to "/quarto".
WORKDIR /quarto

# Copies the Quarto tool and virtual environment created in the first step to the Docker image.
COPY --chown=python:python --from=compile-image /opt/venv /opt/venv
COPY --chown=python:python --from=compile-image quarto-dist/ quarto-dist/

# Creates a symbolic link for the Quarto tool in "/usr/local/bin", so that we can run "quarto" from the command line.
RUN ln -s /quarto/quarto-dist/bin/quarto /usr/local/bin/quarto

# Set the PATH environment variable to include the virtual environment.
ENV PATH="/opt/venv/bin:$PATH"

# Create a virtual environment for Python packages (is this needed)?
RUN python3 -m venv /opt/venv

# Copy necessary files to the docker image.
COPY run.sh .
COPY config.py .
COPY main.py .
COPY *.qmd .

# Change the ownership of the "/quarto" directory to the "python" user and group.
RUN chown python:python /quarto -R

# Setup environment variables.
ENV DENO_DIR=/quarto/deno
ENV XDG_CACHE_HOME=/quarto/cache
ENV XDG_DATA_HOME=/quarto/share

# Set the user for running the Quarto tool to "python" with UID 1069
USER 1069

# Give the "python" user execution rights to the script "run.sh".
RUN chmod +x run.sh

# Specifies the entry point for the Docker image to be the "run.sh" script.
ENTRYPOINT ["./run.sh"]
