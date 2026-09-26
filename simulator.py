import random

class RequestResult:
    def __init__(self, latency, overhead, policy_used):
        self.latency = latency
        self.overhead = overhead
        self.policy_used = policy_used


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.store = {}  # key -> (value, version)

    def read(self, key):
        if key in self.store:
            value, version = self.store[key]
            return value, version
        return None, 0

    def write(self, key, value, new_version):
        self.store[key] = (value, new_version)


class Client:
    def __init__(self, client_id, preferred_node, nodes):
        self.client_id = client_id
        self.preferred_node = preferred_node
        self.nodes = nodes
        self.last_write_version = {}  # key -> version
        self.last_node = preferred_node
        self.last_op = None          # 'read' or 'write'
        self.last_op_key = None

    def should_use_strong(self, key, op_type, migration_happened):
        risk = 0
        if migration_happened:
            risk += 1
        # read-after-write on same key
        if (self.last_op == 'write' and op_type == 'read' and key == self.last_op_key):
            risk += 1
        threshold = 1
        return risk >= threshold


class System:
    def __init__(self, num_nodes, num_keys, replication_factor=2):
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.num_keys = num_keys
        self.replication_factor = replication_factor
        self.key_replicas = {}  # key -> list of node ids
        self.assign_replicas()

    def assign_replicas(self):
        num_nodes = len(self.nodes)
        for k in range(self.num_keys):
            # assign each key to replication_factor distinct nodes at random
            replicas = random.sample(range(num_nodes), self.replication_factor)
            self.key_replicas[k] = replicas

    def handle_request_fixed_strong(self, client, key, op_type):
        # Simple model:
        # - each operation has a base delay
        # - if we need to check/forward to another replica, add overhead
        base_delay = 1.0
        overhead = 0

        replicas = self.key_replicas[key]
        preferred = client.preferred_node

        if op_type == 'write':
            # write: increment version and write to all replicas
            # get current max version among replicas
            max_ver = 0
            for nid in replicas:
                _, ver = self.nodes[nid].read(key)
                if ver is not None and ver > max_ver:
                    max_ver = ver
            new_ver = max_ver + 1

            # write to all replicas (simple, no failure)
            for nid in replicas:
                self.nodes[nid].write(key, random.random(), new_ver)

            # update client's last_write_version
            client.last_write_version[key] = new_ver
            latency = base_delay + len(replicas) * 0.2  # simple model

        else:  # read
            # ensure client sees at least its last written version (RYW-like)
            required_ver = client.last_write_version.get(key, 0)

            # try preferred node first
            value, ver = self.nodes[preferred].read(key)
            if ver is None:
                ver = 0
            if ver < required_ver:
                # need to contact another replica that might have newer version
                overhead += 1
                # simple: pick another replica
                other = [nid for nid in replicas if nid != preferred][0]
                value, ver = self.nodes[other].read(key)

            latency = base_delay + overhead * 0.5

        return RequestResult(latency, overhead, 'fixed_strong')

    def handle_request_adaptive(self, client, key, op_type):
        # Check if client “migrated” (changed preferred node since last request)
        migration_happened = (client.preferred_node != client.last_node)
        use_strong = client.should_use_strong(key, op_type, migration_happened)

        if use_strong:
            res = self.handle_request_fixed_strong(client, key, op_type)
            res.policy_used = 'adaptive_strong'
        else:
            # weak policy: simple, no version checks
            base_delay = 1.0
            overhead = 0
            replicas = self.key_replicas[key]
            preferred = client.preferred_node

            if op_type == 'write':
                # write to all replicas with simple version increment
                max_ver = 0
                for nid in replicas:
                    _, ver = self.nodes[nid].read(key)
                    if ver is not None and ver > max_ver:
                        max_ver = ver
                new_ver = max_ver + 1
                for nid in replicas:
                    self.nodes[nid].write(key, random.random(), new_ver)
                client.last_write_version[key] = new_ver
                latency = base_delay + len(replicas) * 0.2
            else:  # read
                # just read from preferred, no checks
                value, ver = self.nodes[preferred].read(key)
                latency = base_delay

            res = RequestResult(latency, overhead, 'adaptive_weak')

        # update client state
        client.last_node = client.preferred_node
        client.last_op = op_type
        client.last_op_key = key

        return res