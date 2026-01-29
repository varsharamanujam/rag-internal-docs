# rag-internal-docs
End-to-end Retrieval-Augmented Generation (RAG) pipeline for answering questions over internal documents using embeddings and FAISS.
## Problem
Employees struggle to find answers across internal PDFs and documents.

## Architecture
Documents are ingested, chunked, embedded, stored in a vector DB, and retrieved to provide context to an LLM during query time.

## Tech Stack
Python, FAISS, OpenAI API (or equivalent), PDFs

## Future Improvements
Add metadata filtering, better chunking, and evaluation.
