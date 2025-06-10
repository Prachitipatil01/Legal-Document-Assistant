# ollama_inference.py

def get_llm_response(query, clauses):
    """
    Simulated response from a local LLM.
    In real deployment, replace this with an API call to Ollama.
    """
    # For demo, we just search for relevant clauses and echo them
    relevant = [clause for clause in clauses if any(word in clause.lower() for word in query.lower().split())]

    if not relevant:
        return "No relevant information found in the document."

    response = "Here’s what I found:\n\n"
    for i, clause in enumerate(relevant[:3], 1):
        response += f"{i}. {clause.strip()}\n\n"

    return response.strip()
