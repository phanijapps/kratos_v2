import networkx as nx
import matplotlib.pyplot as plt
import io

# --- Main Visualization Logic ---

graphml_file_path = ".vault/memory/episodic_graph.graphml"

# 1. Read the GraphML file content
with open(graphml_file_path, 'r') as file:
    graphml_string = file.read()

# 2. Use io.StringIO to treat the string as a file
graphml_file = io.StringIO(graphml_string)

# 3. Read the GraphML data
#    NetworkX parses the <key> definitions and maps them to node/edge attributes
try:
    G = nx.read_graphml(graphml_file)

    # 4. Set up the plot
    plt.figure(figsize=(15, 10))
    
    # 5. Calculate positions for the nodes using a spring layout
    #    k=0.8 and iterations=50 help spread out the nodes
    pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)

    # 6. Draw the nodes
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='skyblue', alpha=0.8)

    # 7. Draw the node labels (the node IDs)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

    # 8. Draw the edges (which are all self-loops in your data)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=1.5, alpha=0.5, edge_color='gray')

    # 9. Get and draw the edge labels
    #    The key 'd6' was defined with attr.name="label"
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

    # 10. Final plot adjustments and display
    plt.title("Visualization of Your GraphML Data", size=16)
    plt.axis('off')  # Hide the axes
    plt.tight_layout()
    plt.savefig("graph_visualization.png")  # Save the figure as a PNG file

except Exception as e:
    print(f"An error occurred while parsing or drawing the graph: {e}")