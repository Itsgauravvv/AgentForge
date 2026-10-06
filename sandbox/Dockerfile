# Use a lightweight Python environment
FROM python:3.11-slim

# Security: Create a non-root user. 
# We NEVER want the AI running code as the 'root' administrator.
RUN useradd -m -s /bin/bash forge_agent

# Create a workspace directory and give our new user ownership
WORKDIR /workspace
RUN chown forge_agent:forge_agent /workspace

# Switch to the restricted user
USER forge_agent

# This command simply keeps the container running indefinitely in the background
# so our Python backend can connect to it and send commands.
CMD ["tail", "-f", "/dev/null"]