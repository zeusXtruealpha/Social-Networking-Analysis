import grpc
import sqlite3
import threading
from concurrent import futures
import social_graph_pb2
import social_graph_pb2_grpc
import sys
import time
import os

class ShardServicer(social_graph_pb2_grpc.SocialGraphServicer):
    def __init__(self, shard_range):
        self.shard_range = shard_range
        self.shard_id = 1 if shard_range[0] == 1 else 2
        os.makedirs("data", exist_ok=True)
        self.db_file = f"data/shard{self.shard_id}.db"
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()
        print(f"\n🔄 SHARD {self.shard_id} INITIALIZED | Node range: {shard_range}")
        print(f"💾 Database: {self.db_file}")

    def _init_db(self):
        with self.lock:
            # Modified for directed edges
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    timestamp TEXT,
                    sender INTEGER,
                    receiver INTEGER,
                    weight INTEGER,
                    is_self_loop BOOLEAN DEFAULT 0,
                    PRIMARY KEY (timestamp, sender, receiver)
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS shard_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            self.conn.execute("""
                INSERT OR IGNORE INTO shard_metadata VALUES ('range_start', ?)
            """, (str(self.shard_range[0]),))
            self.conn.execute("""
                INSERT OR IGNORE INTO shard_metadata VALUES ('range_end', ?)
            """, (str(self.shard_range[1]),))
            self.conn.commit()

    def _is_in_range(self, node):
        return self.shard_range[0] <= node <= self.shard_range[1]

    def Prepare(self, request, context):
        print(f"\n📥 PREPARE REQUEST | From: {request.node1} To: {request.node2}")
        with self.lock:
            try:
                # Check if at least one node is in this shard
                if not (self._is_in_range(request.node1) or self._is_in_range(request.node2)):
                    print("❌ REJECTED | Nodes outside my range")
                    return social_graph_pb2.Vote(success=False)

                # Check for existing transaction
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM interactions 
                    WHERE timestamp=? AND sender=? AND receiver=?
                """, (request.timestamp, request.node1, request.node2))
                
                if cursor.fetchone():
                    print("⚠️ DUPLICATE TRANSACTION | Already exists")
                    return social_graph_pb2.Vote(success=True)

                # Start transaction
                self.conn.execute("BEGIN IMMEDIATE")
                print("🔒 TRANSACTION LOCK ACQUIRED")
                return social_graph_pb2.Vote(success=True)
            except Exception as e:
                print(f"🚨 PREPARE ERROR: {str(e)}")
                return social_graph_pb2.Vote(success=False)

    def Commit(self, request, context):
        print(f"\n💽 COMMIT REQUEST | From: {request.node1} To: {request.node2}")
        with self.lock:
            try:
                start_time = time.time()
                
                # Handle self-loops (user registration)
                is_self_loop = (request.node1 == request.node2)
                
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO interactions 
                    VALUES (?,?,?,?,?)
                """, (
                    request.timestamp, 
                    request.node1, 
                    request.node2, 
                    request.weight,
                    1 if is_self_loop else 0
                ))
                
                self.conn.commit()
                latency = time.time() - start_time
                action = "👤 USER REGISTERED" if is_self_loop else "💾 MESSAGE RECORDED"
                print(f"{action} | Latency: {latency:.2f}s")
                return social_graph_pb2.Ack(success=True)
            except Exception as e:
                self.conn.rollback()
                print(f"🚨 COMMIT FAILED: {str(e)}")
                return social_graph_pb2.Ack(success=False)

    def GetEdges(self, request, context):
        print(f"\n🔍 EDGE REQUEST | Node: {request.id}")
        edges = []
        with self.lock:
            try:
                cursor = self.conn.cursor()
                # Get both incoming and outgoing edges
                cursor.execute("""
                    SELECT sender, receiver, weight FROM interactions
                    WHERE sender = ? OR receiver = ?
                """, (request.id, request.id))
                
                for row in cursor.fetchall():
                    sender, receiver, weight = row
                    edges.append(social_graph_pb2.Edge(
                        node1=sender, node2=receiver, weight=weight
                    ))
                print(f"📤 SENDING {len(edges)} EDGES")
            except Exception as e:
                print(f"🚨 EDGE QUERY ERROR: {str(e)}")
        
        return social_graph_pb2.EdgeList(edges=edges)

def serve(shard_range, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    social_graph_pb2_grpc.add_SocialGraphServicer_to_server(
        ShardServicer(shard_range), server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"\n🚀 SHARD SERVER STARTED | Port: {port}")
    print("🛑 Press Ctrl+C to stop\n")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python shard.py <start_node> <end_node> <port>")
        print("Example for shard1: python shard.py 1 949 50052")
        print("Example for shard2: python shard.py 950 1899 50053")
        sys.exit(1)
    
    shard_range = (int(sys.argv[1]), int(sys.argv[2]))
    port = int(sys.argv[3])
    serve(shard_range, port)
