import networkx as nx
import matplotlib.pyplot as plt

# -------------------------
# CONFIG
# -------------------------
GEXF_PATH = "./network/movie_net.gexf"
MOVIE = "Forest Gump"
TOP_K = 25        # how many strongest neighbors to keep
MIN_WEIGHT = 1   # ignore very weak edges
SEED = 42

# -------------------------
# LOAD GRAPH
# -------------------------
G = nx.read_gexf(GEXF_PATH)

print("Total nodes:", G.number_of_nodes())
print("Total edges:", G.number_of_edges())

if MOVIE not in G:
    raise ValueError(f"Movie '{MOVIE}' not found in graph")

# -------------------------
# COLLECT & SORT NEIGHBORS
# -------------------------
neighbors = []
for n in G.neighbors(MOVIE):
    w = G[MOVIE][n].get("weight", 1)
    if w >= MIN_WEIGHT:
        neighbors.append((n, w))

# sort by strength
neighbors.sort(key=lambda x: x[1], reverse=True)

# keep top-K
neighbors = neighbors[:TOP_K]

print(f"Using {len(neighbors)} neighbors")

# -------------------------
# BUILD FILTERED EGO GRAPH
# -------------------------
ego = nx.Graph()
ego.add_node(MOVIE)

for n, w in neighbors:
    ego.add_edge(MOVIE, n, weight=w)

# OPTIONAL: add limited 2-hop context (safe)
for n, _ in neighbors[:5]:  # only strongest neighbors
    for nn in G.neighbors(n):
        if nn == MOVIE or nn not in dict(neighbors):
            continue
        w = G[n][nn].get("weight", 1)
        if w >= MIN_WEIGHT:
            ego.add_edge(n, nn, weight=w)

print("Ego nodes:", ego.number_of_nodes())
print("Ego edges:", ego.number_of_edges())

# -------------------------
# VISUALIZATION
# -------------------------
plt.figure(figsize=(12, 12))

pos = nx.spring_layout(
    ego,
    seed=SEED,
    k=0.6
)

# node sizes: center bigger
node_sizes = [
    1600 if n == MOVIE else 600
    for n in ego.nodes()
]

nx.draw_networkx_nodes(
    ego,
    pos,
    node_size=node_sizes,
    node_color="#4aa3df",
    alpha=0.9
)

nx.draw_networkx_edges(
    ego,
    pos,
    alpha=0.35,
    width=1.0
)

nx.draw_networkx_labels(
    ego,
    pos,
    font_size=9
)

plt.title(f"Ego graph for: {MOVIE}", fontsize=14)
plt.axis("off")
plt.show()
