import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random
import time

def create_network(nodes, edges):
    G = nx.DiGraph()
    G.add_nodes_from(range(1, nodes + 1))
    for edge in edges:
        G.add_edge(edge[0], edge[1], bandwidth=edge[2], latency=edge[3], traffic=0)
    return G

def visualize_network(G):
    pos = nx.spring_layout(G)
    fig = go.Figure()

    for node, p in pos.items():
        fig.add_trace(go.Scatter(
            x=[p[0]], y=[p[1]],
            mode='markers+text',
            marker=dict(size=20, color="lightblue"),
            text=str(node),
            textposition="top center"
        ))

    for u, v, data in G.edges(data=True):
        x_coords = [pos[u][0], pos[v][0]]
        y_coords = [pos[u][1], pos[v][1]]
        traffic_ratio = data["traffic"] / data["bandwidth"]
        color = "red" if traffic_ratio > 0.8 else "orange" if traffic_ratio > 0.5 else "green"
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            mode='lines',
            line=dict(color=color, width=2 + traffic_ratio * 8)
        ))

    fig.update_layout(
        title="Network Visualization",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        height=600
    )
    return fig

def update_traffic(G):
    for u, v, data in G.edges(data=True):
        data["traffic"] = random.randint(0, data["bandwidth"])

st.title("Network Digital Twin")
st.sidebar.header("Configuration")

num_nodes = st.sidebar.slider("Number of Nodes", min_value=3, max_value=20, value=6)
num_edges = st.sidebar.slider("Number of Links", min_value=3, max_value=20, value=7)
bandwidth = st.sidebar.slider("Default Bandwidth (Mbps)", min_value=50, max_value=500, value=100)
latency = st.sidebar.slider("Default Latency (ms)", min_value=1, max_value=50, value=10)
fault_threshold = st.sidebar.slider("Fault Prediction Threshold (%)", min_value=50, max_value=100, value=80)

random_edges = [
    (random.randint(1, num_nodes), random.randint(1, num_nodes), bandwidth, latency)
    for _ in range(num_edges)
]

G = create_network(num_nodes, random_edges)

if st.sidebar.button("Simulate Network"):
    step = 0
    while step < 10:
        step += 1
        st.sidebar.text(f"Simulating Step {step}")
        update_traffic(G)

        fig = visualize_network(G)
        st.plotly_chart(fig, use_container_width=True)

        faults = []
        for u, v, data in G.edges(data=True):
            if data["traffic"] > fault_threshold / 100 * data["bandwidth"]:
                faults.append((u, v, data["traffic"], "High Traffic"))

        if faults:
            st.sidebar.subheader("Predicted Faults")
            for fault in faults:
                st.sidebar.write(f"Link {fault[0]} -> {fault[1]}: {fault[2]} Mbps Traffic")
        else:
            st.sidebar.write("No Faults Detected")

        time.sleep(1)  
