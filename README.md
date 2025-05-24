# Social Network Analysis System

// ... existing code ...

## Usage

1. Start the coordinator:
```bash
python coordinator.py
or
python3 coordinator.py
```

2. Start shard nodes:
```bash
python shard.py --port <port_number>
or
python3 shard.py --port <port_number>
```

3. Use the client to interact with the system:
```bash
python graph_client.py
or
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
