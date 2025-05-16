import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from graph.dgraph_query import build_graph
from graph.mcts_reasoning import MCTS
from llm.gemini_prompt import ask_gemini
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "medical-graphrag"
EMBED_DIM = 384

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(INDEX_NAME)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def vector_search(query, top_k=3):
    xq = model.encode(query).tolist()
    results = index.query(vector=xq, top_k=top_k, include_metadata=True)
    return [match["metadata"]["text"] for match in results["matches"]]

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

def run_pipeline(user_query, start_concept=None, target_concept=None):
    docs = vector_search(user_query)

    reasoning = ""
    if start_concept and target_concept:
        reasoning = graph_reasoning(start_concept, target_concept)

    context = "\n".join(docs)
    if reasoning:
        context += f"\n\nGraph Reasoning Path: {reasoning}"

    print("📌 Querying Gemini...\n")
    answer = ask_gemini(context, user_query)
    print("🔍 Gemini Response:\n")
    print(answer)

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
        print("❌ Failed to parse concepts:", e)
        return None, None

if __name__ == "__main__":
    query = "What treats MDR-Tuberculosis and what are its side effects?"
    start, end = extract_concepts_with_gemini(query)
    run_pipeline(user_query=query, start_concept=start, target_concept=end)
