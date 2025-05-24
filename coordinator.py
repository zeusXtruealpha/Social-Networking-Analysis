import grpc
import social_graph_pb2
import social_graph_pb2_grpc
from concurrent import futures
import threading
import raft
import time

class Coordinator(social_graph_pb2_grpc.SocialGraphServicer):
    def __init__(self):
        self.shards = {
            "shard1": "localhost:50052",  # Users 1-949
            "shard2": "localhost:50053"   # Users 950-1899
        }
        self.leader = False
        self.raft = raft.RaftNode(self)  # This now starts as leader immediately
        self.transaction_log = []
        self.lock = threading.Lock()
        print("✅ Coordinator initialized with shards:", self.shards)

    def is_leader(self):
        return True  # Always true in single-node mode

    def InsertData(self, request, context):
        print(f"\n📨 INSERT REQUEST | From: {request.node1} To: {request.node2} | Weight: {request.weight}")
        
        # Track transaction
        tx_id = len(self.transaction_log) + 1
        self.transaction_log.append({
            "id": tx_id,
            "nodes": (request.node1, request.node2),
            "status": "pending"
        })
        
        # Determine involved shards (949 is the midpoint)
        involved_shards = set()
        if request.node1 <= 949 or request.node2 <= 949:
            involved_shards.add("shard1")
        if request.node1 > 949 or request.node2 > 949:
            involved_shards.add("shard2")
        print(f"🔀 Routing to shards: {involved_shards}")

        # Two-Phase Commit
        print("🔄 Starting 2PC Protocol...")
        
        # Phase 1: Prepare
        prepared = []
        for shard in involved_shards:
            try:
                print(f"  📢 PREPARE PHASE | Contacting {shard}...")
                channel = grpc.insecure_channel(self.shards[shard])
                stub = social_graph_pb2_grpc.SocialGraphStub(channel)
                start_time = time.time()
                
                response = stub.Prepare(social_graph_pb2.Transaction(
                    timestamp=request.timestamp,
                    node1=request.node1,
                    node2=request.node2,
                    weight=request.weight
                ))
                
                latency = time.time() - start_time
                if response.success:
                    prepared.append(shard)
                    print(f"  👍 {shard} PREPARED SUCCESSFULLY | Latency: {latency:.2f}s")
                else:
                    print(f"  ❌ {shard} PREPARE FAILED | Latency: {latency:.2f}s")
            except Exception as e:
                print(f"  🚨 COMMUNICATION ERROR with {shard}: {str(e)}")

        # Phase 2: Commit (if all prepared)
        if len(prepared) == len(involved_shards):
            print("✅ ALL SHARDS PREPARED | Proceeding to COMMIT...")
            for shard in prepared:
                try:
                    print(f"  💾 COMMITTING to {shard}...")
                    channel = grpc.insecure_channel(self.shards[shard])
                    stub = social_graph_pb2_grpc.SocialGraphStub(channel)
                    start_time = time.time()
                    
                    response = stub.Commit(social_graph_pb2.Transaction(
                        timestamp=request.timestamp,
                        node1=request.node1,
                        node2=request.node2,
                        weight=request.weight
                    ))
                    
                    latency = time.time() - start_time
                    if response.success:
                        print(f"  🎉 {shard} COMMIT SUCCESS | Latency: {latency:.2f}s")
                    else:
                        print(f"  ❌ {shard} COMMIT FAILED | Latency: {latency:.2f}s")
                except Exception as e:
                    print(f"  🚨 COMMIT ERROR with {shard}: {str(e)}")
            
            self.transaction_log[-1]["status"] = "committed"
            return social_graph_pb2.Ack(success=True, message="Transaction committed")
        else:
            print("❌ PREPARE PHASE FAILED | Aborting transaction")
            self.transaction_log[-1]["status"] = "aborted"
            return social_graph_pb2.Ack(success=False, message="Prepare phase failed")

    def GetEdges(self, request, context):
        print(f"\n🔍 EDGE REQUEST | Node: {request.id}")
        edges = []
        
        # Check both shards since edges might be in either
        for shard in ["shard1", "shard2"]:
            try:
                print(f"  🔎 Querying {shard}...")
                channel = grpc.insecure_channel(self.shards[shard])
                stub = social_graph_pb2_grpc.SocialGraphStub(channel)
                
                response = stub.GetEdges(social_graph_pb2.NodeId(id=request.id))
                edges.extend(response.edges)
                print(f"  📥 Received {len(response.edges)} edges from {shard}")
            except Exception as e:
                print(f"  🚨 ERROR querying {shard}: {str(e)}")
        
        return social_graph_pb2.EdgeList(edges=edges)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    coordinator = Coordinator()
    social_graph_pb2_grpc.add_SocialGraphServicer_to_server(
        coordinator, server)
    server.add_insecure_port('[::]:50051')
    print("\n🚀 COORDINATOR SERVER STARTED")
    print("📡 Listening on port 50051")
    print("🛑 Press Ctrl+C to stop\n")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()