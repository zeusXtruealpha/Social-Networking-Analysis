# Social Network Analysis System

Welcome to our Social Network Analysis System! This project implements a distributed system for analyzing and managing social network graphs using gRPC and the Raft consensus protocol. It's designed to handle large-scale social network data efficiently and reliably.

## Features

### Distributed Graph Management
- Distributed storage and processing of social network data
- Fault-tolerant architecture using Raft consensus protocol
- Efficient edge and node management
- Real-time graph updates and queries

### Data Analysis
- Social network graph visualization
- Edge weight analysis
- Node relationship tracking
- Network metrics computation

### System Architecture
- Coordinator-based architecture for request management
- Sharded data storage for scalability
- Consensus-based replication for reliability
- gRPC-based communication between nodes

## Technical Stack
- Python for core implementation
- gRPC for inter-service communication
- NetworkX for graph operations
- Matplotlib for visualization
- SQLite for local data storage

## Prerequisites
- Python 3.6+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/social-networking-analysis.git
cd social-networking-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup script:
```bash
./setup.sh
```

## Project Structure
```
.
├── coordinator.py          # Main coordinator service
├── shard.py               # Shard management implementation
├── raft.py               # Raft consensus protocol implementation
├── social_graph.proto    # Protocol buffer definitions
├── graph_client.py       # Client implementation
├── load_data.py          # Data loading utilities
└── requirements.txt      # Project dependencies
```

## Key Components

### Coordinator Service
- Manages client requests
- Coordinates between shards
- Handles load balancing
- Maintains system state

### Shard Management
- Distributes data across multiple nodes
- Handles data replication
- Manages shard operations

### Raft Implementation
- Leader election
- Log replication
- State machine execution
- Fault tolerance

## Usage

1. Start the coordinator:
```bash
python coordinator.py
```
or
```bash
python3 coordinator.py
```

2. Start shard nodes:
```bash
python shard.py --port <port_number>
```
or
```bash
python3 shard.py --port <port_number>
```

3. Use the client to interact with the system:
```bash
python graph_client.py
```
or
```bash
python3 graph_client.py
```

## Dependencies
```
grpcio==1.48.2
grpcio-tools==1.48.2
networkx==2.8.8
matplotlib==3.6.2
sqlite3==3.39.4
tqdm==4.64.1
```

## Contributing
We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact
For any questions or suggestions, please reach out to:
- Email: niranjan.galla.7@gmail.com

## License
This project is licensed under the MIT License - see the LICENSE file for details.
