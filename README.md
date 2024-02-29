# Build with GitHub Actions: MinIO Weaviate Python

#### Workflow Status Badges:
[![Docker-Compose Build Test](https://github.com/Cdaprod/minio-weaviate/actions/workflows/docker-compose-build-test.yml/badge.svg)](https://github.com/Cdaprod/minio-weaviate/actions/workflows/docker-compose-build-test.yml)

[![Update README with Directory Tree](https://github.com/Cdaprod/minio-weaviate-python/actions/workflows/update_readme.yml/badge.svg)](https://github.com/Cdaprod/minio-weaviate-python/actions/workflows/update_readme.yml)

## Current Directory Tree Structure
The following directory tree is programatically generated to provide an overview of the repos structure (by using `.github/workflows/update_readme.yml` and `.github/scripts/update_readme.py` and is ran on `push` to `main`):

<!-- DIRECTORY_TREE_START -->
```
.
├── DIRECTORY_TREE.txt
├── README.md
├── app
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── logs
│   │   └── python_logs.txt
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yaml
├── minio
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── logs
│       └── minio_logs.txt
└── weaviate
    ├── data.json
    ├── logs
    │   └── weaviate_logs.txt
    └── schema.json

6 directories, 14 files

```
<!-- DIRECTORY_TREE_END -->

## Introduction
This project serves as a template for building [specific type of projects] with a pre-configured setup including `/app/`, `/minio/`, and `/weaviate/` directories.

## How to Use This Template
To start a new project based on this template:

1. Click the "Use this template" button on the GitHub repository page.
2. Choose a name for your new repository and select "Create repository from template".
3. Clone your new repository to your local machine and begin customizing.

## Configuration
- **App**: Instructions on configuring the `/app/` directory.
- **Minio**: Steps to set up the `/minio/` directory.
- **Weaviate**: Guidelines for initializing the `/weaviate/` component.

Based on the available information from the MinIO and Weaviate documentation, here are the specific commands and configurations for setting up MinIO and Weaviate using Dockerfile and `entrypoint.sh`. However, the exact details for MinIO were not found in the recent search, so I'll provide a general approach based on common practices.

### MinIO Setup using Dockerfile and entrypoint.sh

To configure a MinIO server using Docker, you typically start by creating a `Dockerfile` that specifies the MinIO server image and any necessary environment variables. The `entrypoint.sh` script is used to customize the startup behavior of the MinIO server.

#### Dockerfile for MinIO

```Dockerfile
FROM minio/minio
COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
```

#### entrypoint.sh for MinIO

```bash
#!/bin/sh
# Custom startup script for MinIO

# Initialize MinIO server with specified directories or buckets
minio server /data --console-address ":9001"
```

You may need to adjust the `minio server` command with additional flags or environment variables as per your configuration requirements, such as enabling TLS, setting access and secret keys, etc.

### Weaviate Setup using Dockerfile and entrypoint.sh

The Weaviate documentation provides insights into running Weaviate with Docker, including using `docker-compose` for orchestrating multiple services. For a single-node setup or development purposes, you can encapsulate the configuration in a Dockerfile and an entrypoint script.

#### Dockerfile for Weaviate

```Dockerfile
FROM semitechnologies/weaviate
COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
```

#### entrypoint.sh for Weaviate

```bash
#!/bin/bash
# Custom startup script for Weaviate

# Start Weaviate with a specific configuration
# You can customize this command based on your setup requirements
weaviate start -d
```

In practice, you'd replace `weaviate start -d` with the actual command to start Weaviate, configuring it with environment variables or command-line options as needed for your application. Since Weaviate's setup can vary significantly based on modules and integrations, refer to the [Weaviate documentation](https://weaviate.io/developers/weaviate/current/) for specific configuration details.

### General Notes

- Ensure that both `entrypoint.sh` scripts are executable (`chmod +x entrypoint.sh`) before building your Docker images.
- Adapt the MinIO and Weaviate commands in the `entrypoint.sh` scripts according to your specific needs, such as configuring network settings, security parameters, or enabling specific modules.
- For both services, you might need to configure network settings in `docker-compose.yml` if you're orchestrating multiple containers to ensure they can communicate with each other and with any dependent services.

Remember to consult the official MinIO and Weaviate documentation for the most up-to-date and detailed setup instructions, as configurations can change with new software versions.

## Accessing Specific Versions

To clone a specific version of this project, use the following command, replacing `tag_name` with the desired version tag:

```bash
git clone --branch tag_name --depth 1 https://github.com/cdaprod/minio-weaviate-langchain.git
```

## Contributing
We welcome contributions! Please read our contributing guidelines on how to propose changes.
