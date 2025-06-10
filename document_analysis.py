# document_analysis.py
import re
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def extract_clauses(text):
    clauses = re.findall(r"(Clause\s+\d+[:.\-].*?)(?=\nClause\s+\d+[:.\-]|\Z)", text, re.DOTALL | re.IGNORECASE)
    if not clauses:
        clauses = text.split("\n\n")
    return [cl.strip() for cl in clauses if len(cl.strip()) > 20]


def find_risks(clauses):
    risky_terms = ['penalty', 'termination', 'breach', 'indemnity', 'arbitration', 'liable', 'damages']
    risks = []
    for clause in clauses:
        found_terms = [term for term in risky_terms if term in clause.lower()]
        if found_terms:
            confidence = round(len(found_terms) / len(risky_terms) * 100, 2)
            risks.append((found_terms, clause, confidence))
    return risks


def summarize_clause(clause):
    sentences = re.split(r'(?<=[.!?]) +', clause)
    if len(sentences) >= 2:
        return ' '.join(sentences[:2])
    return clause[:100] + ('...' if len(clause) > 100 else '')


# ollama_inference.py

def run_llm_query(query):
    # Simulate call to local LLM (Ollama)
    # In production, replace this with actual Ollama local model API call
    return f"[Simulated Answer from LLM for Query: {query}]"

def citation_tracking(clause):
    return ["Case A vs B (2020)", "Contract Law Handbook - Section 3"]  # Dummy citations
