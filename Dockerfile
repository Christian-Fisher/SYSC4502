FROM python:3
COPY .devcontainer/bashsetup.sh /tmp/library-scripts/

# Install needed packages and setup non-root user. Use a separate RUN statement to add your own dependencies.
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    # Install common packages, non-root user
    && bash /tmp/library-scripts/bashsetup.sh "${USERNAME}" "${USER_UID}" "${USER_GID}" "true" \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Development dependencies
RUN pip install pylint

# Remove library scripts for final image
RUN rm -rf /tmp/library-scripts

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .