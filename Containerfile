# MCP Google Search Console CrunchTools Container
# Built on Hummingbird Python image (Red Hat UBI-based) for enterprise security
#
# Build:
#   podman build -t quay.io/crunchtools/mcp-google-search-console .
#
# Run:
#   podman run --env-file ~/.config/mcp-env/mcp-google-search-console.env \
#     quay.io/crunchtools/mcp-google-search-console

# Use Hummingbird Python image (Red Hat UBI-based with Python pre-installed)
FROM quay.io/hummingbird/python:latest

# Labels for container metadata
LABEL name="mcp-google-search-console-crunchtools" \
      version="0.1.0" \
      summary="Secure MCP server for Google Search Console analytics, sitemaps, and URL inspection" \
      description="A security-focused MCP server for Google Search Console built on Red Hat UBI" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-google-search-console" \
      io.k8s.display-name="MCP Google Search Console CrunchTools" \
      io.openshift.tags="mcp,google-search-console,seo" \
      org.opencontainers.image.source="https://github.com/crunchtools/mcp-google-search-console" \
      org.opencontainers.image.description="Secure MCP server for Google Search Console" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and dependencies
RUN pip install --no-cache-dir .

# Verify installation
RUN python -c "from mcp_google_search_console_crunchtools import main; print('Installation verified')"

# Default: stdio transport (use -i with podman run)
# HTTP:    --transport streamable-http (use -d -p 8017:8017 with podman run)
EXPOSE 8017
ENTRYPOINT ["python", "-m", "mcp_google_search_console_crunchtools"]
