# Use the official MinIO image as the base
FROM minio/minio

# Expose both the API and Console ports
EXPOSE 9000
EXPOSE 9001

# Copy entrypoint.sh into the container
COPY entrypoint.sh /entrypoint.sh

# Make the script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint to run the script
ENTRYPOINT ["/entrypoint.sh"]