# Patent Agent Data Repository

This repository contains training data, vector stores, and large files for the patent agent.

## Structure
- `corpus/` - Training corpus and knowledge base files
- `vectorstore/` - FAISS indices and embedding files  
- `knowledge_base/` - Structured knowledge files
- `models/` - Local AI models (GGUF format)
- `datasets/` - Training and evaluation datasets

## Git LFS Configuration
This repository uses Git LFS for large files. All vector stores, models, and datasets are tracked with LFS.

## Usage
This repository is used as a submodule in the main patent-agent repository.
