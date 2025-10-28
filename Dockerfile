# Multi-stage build for XLeRobot NPU Converter
# Stage 1: Base environment with Ubuntu 20.04 and Python 3.10
FROM ubuntu:20.04 as base

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Update package lists and install basic dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    git \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.10 and related packages
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-dev python3.10-distutils python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Create symbolic links for python3.10
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.10 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3.10 1

# Upgrade pip and install basic Python packages
RUN python -m pip install --upgrade pip setuptools wheel

# Stage 2: Application environment
FROM base as application

# Create non-root user for security
ARG USERNAME=npuuser
ARG USER_UID=1000
ARG USER_GID=1000

# Create group and user
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Set working directory
WORKDIR /app

# Create requirements files first to leverage Docker layer caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Create Horizon X5 toolchain installation directory
RUN mkdir -p /opt/horizon

# Copy Horizon X5 installation script
COPY scripts/horizon/install_toolchain.sh /tmp/install_toolchain.sh

# Make the script executable
RUN chmod +x /tmp/install_toolchain.sh

# Copy Horizon X5 configuration
COPY config/horizon-x5.yaml /tmp/horizon-x5.yaml

# Set environment variables for installation
ENV HORIZON_DOWNLOAD_URL="https://horizon-x5.example.com/toolchain.tar.gz"
ENV HORIZON_CHECKSUM_FILE="placeholder_checksum"

# Install Horizon X5 BPU toolchain
RUN /tmp/install_toolchain.sh

# Set environment variables for Horizon X5 toolchain
ENV HORIZON_TOOLCHAIN_ROOT="/opt/horizon"
ENV PATH="${HORIZON_TOOLCHAIN_ROOT}/bin:${PATH}"
ENV LD_LIBRARY_PATH="${HORIZON_TOOLCHAIN_ROOT}/lib:${LD_LIBRARY_PATH}"

# Create environment profile file
RUN echo 'export HORIZON_TOOLCHAIN_ROOT="/opt/horizon"' > /etc/profile.d/horizon-toolchain.sh && \
        echo 'export PATH="${HORIZON_TOOLCHAIN_ROOT}/bin:${PATH}"' >> /etc/profile.d/horizon-toolchain.sh && \
        echo 'export LD_LIBRARY_PATH="${HORIZON_TOOLCHAIN_ROOT}/lib:${LD_LIBRARY_PATH}"' >> /etc/profile.d/horizon-toolchain.sh

# Copy application code (will be added in future stories)
# COPY src/ ./src/
# COPY config/ ./config/

# Change ownership of the application directory
RUN chown -R $USERNAME:$USER_GID /app

# Switch to non-root user
USER $USERNAME

# Set default command
CMD ["python", "--version"]

# Labels for metadata
LABEL maintainer="XLeRobot Team"
LABEL version="1.0.0"
LABEL description="XLeRobot NPU Converter - Docker environment with Ubuntu 20.04 and Python 3.10"