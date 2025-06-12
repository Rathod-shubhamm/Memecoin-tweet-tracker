from collections import defaultdict, deque

class Network:
    def __init__(self, n):
        self.graph = defaultdict(dict)
        self.n = n

    def add_edge(self, u, v, cost):
        self.graph[u][v] = cost
        self.graph[v][u] = cost

    def update_cost(self, u, v, new_cost):
        self.graph[u][v] = new_cost
        self.graph[v][u] = new_cost

    def transmission_cost(self, start, end):
        visited = [False] * (self.n + 1)
        queue = deque([(start, 0)])
        while queue:
            node, cost = queue.popleft()
            if node == end:
                return cost
            if visited[node]:
                continue
            visited[node] = True
            for neighbor, edge_cost in self.graph[node].items():
                if not visited[neighbor]:
                    queue.append((neighbor, cost + edge_cost))
        return -1

class Solution:
    def processNetwork(self):
        import sys
        input = sys.stdin.readline
        total_cost = 0

        while True:
            line = ''
            while line.strip() == '':
                line = input()
                if not line:
                    return
            if line.strip() == '0':
                break

            N = int(line.strip())
            R = int(input().strip())
            network = Network(N)

            for _ in range(N - 1):
                u, v, cost = map(int, input().strip().split())
                network.add_edge(u, v, cost)

            while True:
                query = input().strip()
                if query == '0':
                    break
                parts = query.split()
                if parts[0] == '1':
                    A, B = int(parts[1]), int(parts[2])
                    total_cost += network.transmission_cost(A, B)
                elif parts[0] == '2':
                    X, Y, Z = int(parts[1]), int(parts[2]), int(parts[3])
                    network.update_cost(X, Y, Z)

        print(total_cost)

def driver():
    sol = Solution()
    sol.processNetwork()

if __name__ == "__main__":
    driver()
