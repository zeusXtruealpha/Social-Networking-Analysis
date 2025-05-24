#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Generate gRPC code
python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/social_graph.proto

# Create data directories
mkdir -p data/shard1 data/shard2

echo "✅ Setup complete"
