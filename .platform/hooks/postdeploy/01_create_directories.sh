#!/bin/bash
# Create necessary directories for persistent data

# Create data directory (will be on EFS)
mkdir -p /var/app/current/data
mkdir -p /var/app/current/data/expert_embeddings
mkdir -p /var/app/current/data/literature_embeddings

# Set permissions
chmod -R 777 /var/app/current/data

echo "Data directories created successfully"
