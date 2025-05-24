import grpc
import social_graph_pb2
import social_graph_pb2_grpc
import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph():
    print("\n📊 GRAPH VISUALIZATION CLIENT")
    channel = grpc.insecure_channel('localhost:50051')
    stub = social_graph_pb2_grpc.SocialGraphStub(channel)

    node_id = int(input("Enter node ID to visualize (1-1899): "))
    response = stub.GetEdges(social_graph_pb2.NodeId(id=node_id))

    G = nx.DiGraph()  # Changed to directed graph
    for edge in response.edges:
        G.add_edge(edge.node1, edge.node2, weight=edge.weight)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', 
            node_size=800, arrowsize=20)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title(f"Connections for Node {node_id}")
    plt.show()
    print("🎨 Visualization complete!")

if __name__ == '__main__':
    visualize_graph()