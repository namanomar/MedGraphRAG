import os
import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from graph.dgraph_query import build_graph
from graph.mcts_reasoning import MCTS
from llm.gemini_prompt import ask_gemini
from dotenv import load_dotenv

load_dotenv()

# Constants
INDEX_NAME = "medical-graphrag"
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(INDEX_NAME)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Vector Search
def vector_search(query, top_k=3):
    xq = model.encode(query).tolist()
    results = index.query(vector=xq, top_k=top_k, include_metadata=True)
    return [match["metadata"]["text"] for match in results["matches"]]

# Graph Reasoning
def graph_reasoning(start_node_name, target_node_name):
    graph = build_graph()
    name_to_uid = {node.name: uid for uid, node in graph.items()}
    start_uid = name_to_uid.get(start_node_name)
    target = target_node_name

    if not start_uid:
        return f"Start node '{start_node_name}' not found in graph."

    mcts = MCTS(graph)
    path = mcts.traverse(start_uid=start_uid, target_name=target)

    return (
        " -> ".join([graph[n].name for n in path])
        if path else f"No path found from '{start_node_name}' to '{target_node_name}'."
    )

# Concept Extraction
def extract_concepts_with_gemini(query):
    prompt = f"""
Extract the most relevant start and target concepts (key medical entities) from the following question.
Respond ONLY in the format: start_concept: <value>, target_concept: <value>

Question: "{query}"
"""
    response = ask_gemini(prompt, query)

    try:
        lines = response.strip().split(",")
        start = lines[0].split(":", 1)[1].strip()
        target = lines[1].split(":", 1)[1].strip()
        return start, target
    except Exception as e:
        return None, None

# Final Answer Polish
def polish_with_gemini(raw_answer):
    prompt = f"Polish and present the following answer clearly for a medical professional:\n\n{raw_answer}"
    return ask_gemini(prompt, raw_answer)

# Streamlit UI
st.set_page_config(page_title="🧠 Medical GraphRAG", layout="wide")
st.title("🧬 Medical GraphRAG Assistant")

query = st.text_input("Enter your medical question:", placeholder="e.g. What treats MDR-Tuberculosis and what are its side effects?")

if query:
    with st.spinner("Analyzing with Gemini..."):
        start, end = extract_concepts_with_gemini(query)

    st.markdown(f"**🔎 Extracted Concepts:**\n- Start: `{start}`\n- Target: `{end}`")

    with st.spinner("Running vector search..."):
        docs = vector_search(query)

    with st.spinner("Running graph reasoning..."):
        reasoning_path = graph_reasoning(start, end) if start and end else ""

    context = "\n".join(docs)
    if reasoning_path:
        context += f"\n\nGraph Reasoning Path: {reasoning_path}"

    with st.spinner("Querying Gemini..."):
        raw_answer = ask_gemini(context, query)

    with st.spinner("Polishing final response..."):
        polished_answer = polish_with_gemini(raw_answer)

    st.subheader("📌 Final Answer")
    st.markdown(polished_answer)

    with st.expander("🧠 Raw Gemini Response"):
        st.text(raw_answer)

    with st.expander("🕸️ Graph Reasoning Path"):
        st.text(reasoning_path)

    with st.expander("📚 Retrieved Context Docs"):
        for doc in docs:
            st.markdown(f"- {doc}")
