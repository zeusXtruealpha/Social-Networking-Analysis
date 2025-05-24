import threading
import time
import random
import grpc
import social_graph_pb2
import social_graph_pb2_grpc

class RaftNode:
    def __init__(self, coordinator):
        self.state = "leader"  # Start as leader immediately
        self.current_term = 1
        self.coordinator = coordinator
        self.coordinator.leader = True
        print("\n🛶 RAFT NODE INITIALIZED")
        print(f"⚡ Initial state: LEADER (single-node mode)")
        print(f"🔢 Current term: {self.current_term}")

    def start_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()
        self.election_timer = threading.Timer(
            self.election_timeout, self.start_election)
        self.election_timer.start()

    def start_election(self):
        if self.state != "leader":
            self.state = "candidate"
            self.current_term += 1
            self.voted_for = "self"
            self.votes_received = 1
            print(f"\n🎯 ELECTION STARTED | Term: {self.current_term}")
            
            threads = []
            for node in self.other_nodes:
                t = threading.Thread(target=self.request_vote, args=(node,))
                threads.append(t)
                t.start()
            
            time.sleep(1.0)
            
            if self.votes_received > len(self.other_nodes) / 2:
                self.become_leader()
            else:
                print(f"❌ ELECTION FAILED | Term: {self.current_term}")
                self.state = "follower"
                self.start_election_timer()

    def request_vote(self, node_address):
        try:
            channel = grpc.insecure_channel(node_address)
            stub = social_graph_pb2_grpc.SocialGraphStub(channel)
            response = stub.RequestVote(social_graph_pb2.VoteRequest(
                term=self.current_term,
                candidate_id="self"
            ))
            
            if response.vote_granted:
                with threading.Lock():
                    self.votes_received += 1
        except Exception as e:
            print(f"🚨 Vote request failed to {node_address}: {str(e)}")

    def become_leader(self):
        self.state = "leader"
        self.coordinator.leader = True
        print(f"\n👑 LEADER ELECTED | Term: {self.current_term}")
        self.start_heartbeat()

    def start_heartbeat(self):
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
        self.send_heartbeat()

    def send_heartbeat(self):
        if self.state == "leader":
            print(f"💓 Sending heartbeat (Term: {self.current_term})")
            threads = []
            for node in self.other_nodes:
                t = threading.Thread(target=self.send_single_heartbeat, args=(node,))
                threads.append(t)
                t.start()
            
            self.heartbeat_timer = threading.Timer(1.0, self.send_heartbeat)
            self.heartbeat_timer.start()

    def send_single_heartbeat(self, node_address):
        try:
            channel = grpc.insecure_channel(node_address)
            stub = social_graph_pb2_grpc.SocialGraphStub(channel)
            stub.AppendEntries(social_graph_pb2.AppendEntriesRequest(
                term=self.current_term,
                leader_id="self"
            ))
        except Exception as e:
            print(f"🚨 Heartbeat failed to {node_address}: {str(e)}")

    def receive_heartbeat(self, term, leader_id):
        if term > self.current_term:
            self.current_term = term
            if self.state != "follower":
                print(f"🔽 DEMOTED TO FOLLOWER | Term: {self.current_term}")
            self.state = "follower"
            self.voted_for = None
            self.start_election_timer()
        
        if self.state == "follower":
            self.start_election_timer()