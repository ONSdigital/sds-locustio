# Copyright 2022 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-alpine

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy the pyproject and lockfile first (for better caching)
ADD pyproject.toml uv.lock ./

# Install the project's dependencies using the lockfile and settings
# We use docker mounts to cache the UV cache acrross builds (This speeds up multiple Docker builds)
# We also use bind mounts for uv.lock and pyproject.toml to ensure that the cache is invalidated when they change
RUN uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD performance_tests /app
RUN uv sync --frozen --no-dev

# Expose the required Locust ports
EXPOSE 5557 5558 8089

# Install bash. This is required for the run.sh script to execute properly, as it uses bash-specific syntax.
# Alpine Linux does not include bash by default, so we need to add it explicitly.
RUN apk add --no-cache bash

# Set script to be executable
RUN chmod 755 /app/run.sh

# Start Locust using LOCUS_OPTS environment variable
ENTRYPOINT ["/app/run.sh"]