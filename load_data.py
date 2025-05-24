import grpc
import social_graph_pb2
import social_graph_pb2_grpc
import time
from tqdm import tqdm

def parse_line(line):
    """Parse dataset line with format: "timestamp" sender receiver weight"""
    try:
        parts = line.strip().replace('"', '').split()
        timestamp = f"{parts[0]} {parts[1]}"
        sender = int(parts[2])
        receiver = int(parts[3])
        weight = int(parts[4]) if len(parts) > 4 else 1
        return timestamp, sender, receiver, weight
    except Exception as e:
        print(f"\n🚨 PARSING ERROR: {str(e)} in line: {line.strip()}")
        return None

def load_data(file_path):
    print("\n📂 LOADING DATASET:", file_path)
    channel = grpc.insecure_channel('localhost:50051')
    stub = social_graph_pb2_grpc.SocialGraphStub(channel)

    with open(file_path) as f:
        lines = f.readlines()

    successful = 0
    start_time = time.time()

    for i, line in enumerate(tqdm(lines, desc="Processing"), 1):
        if line.strip():
            parsed = parse_line(line)
            if not parsed:
                continue

            timestamp, sender, receiver, weight = parsed

            try:
                response = stub.InsertData(social_graph_pb2.Transaction(
                    timestamp=timestamp,
                    node1=sender,
                    node2=receiver,
                    weight=weight
                ))

                if response.success:
                    successful += 1
                else:
                    tqdm.write(f"❌ Insert failed for line {i}: {sender}->{receiver}")
            except Exception as e:
                tqdm.write(f"🚨 Error on line {i}: {str(e)}")

            time.sleep(0.01)  # Rate limiting

    total_time = time.time() - start_time
    print("\n📊 LOADING SUMMARY")
    print(f"✅ Successful inserts: {successful}/{len(lines)}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📈 Throughput: {successful/max(1,total_time):.2f} records/sec")

if __name__ == '__main__':
    load_data('OCnodeslinks_chars.txt')