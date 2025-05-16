import google.generativeai as genai

genai.configure(api_key="AIzaSyBp7_rESPYpMJBxzccmxwPSl0WETaDE0L4")
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(context: str, query: str) -> str:
    prompt = f"""Context: {context}\n\nUser Question: {query}\n\nAnswer: """
    response = model.generate_content(prompt)
    return response.text
