import random
import csv
from simulator import System, Client

def run_experiment(num_nodes=4, num_clients=20, num_keys=10,
                   num_requests=1000, read_ratio=0.8,
                   migration_prob=0.1, policy='fixed_strong',
                   result_file=None):

    system = System(num_nodes, num_keys, replication_factor=2)
    clients = []
    for c in range(num_clients):
        pref = random.randint(0, num_nodes - 1)
        clients.append(Client(c, pref, system.nodes))

    results = []

    for req_id in range(num_requests):
        client = random.choice(clients)

        # possibly migrate
        if random.random() < migration_prob:
            old_pref = client.preferred_node
            new_pref = random.randint(0, num_nodes - 1)
            client.preferred_node = new_pref

        key = random.randint(0, num_keys - 1)
        op_type = 'read' if random.random() < read_ratio else 'write'

        if policy == 'fixed_strong':
            res = system.handle_request_fixed_strong(client, key, op_type)
        elif policy == 'adaptive':
            res = system.handle_request_adaptive(client, key, op_type)
        else:
            raise ValueError("Unknown policy")

        results.append(res)

    # compute averages
    avg_latency = sum(r.latency for r in results) / len(results)
    avg_overhead = sum(r.overhead for r in results) / len(results)

    if result_file:
        # save detailed results to CSV
        with open(result_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['request_id', 'policy_used', 'latency', 'overhead'])
            for i, r in enumerate(results):
                writer.writerow([i, r.policy_used, r.latency, r.overhead])

    return avg_latency, avg_overhead


if __name__ == '__main__':
    # Example: run two policies and print results
    lat_fixed, oh_fixed = run_experiment(
        num_nodes=4,
        num_clients=20,
        num_keys=10,
        num_requests=1000,
        read_ratio=0.8,
        migration_prob=0.1,
        policy='fixed_strong',
        result_file='results/fixed_strong.csv'
    )

    lat_adaptive, oh_adaptive = run_experiment(
        num_nodes=4,
        num_clients=20,
        num_keys=10,
        num_requests=1000,
        read_ratio=0.8,
        migration_prob=0.1,
        policy='adaptive',
        result_file='results/adaptive.csv'
    )

    print("Fixed strong  -> avg latency:", round(lat_fixed, 3), "avg overhead:", round(oh_fixed, 3))
    print("Adaptive      -> avg latency:", round(lat_adaptive, 3), "avg overhead:", round(oh_adaptive, 3))