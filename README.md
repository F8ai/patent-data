# Patent Agent Data Repository

This repository contains training data, scripts, and resources for the Patent Agent specializing in cannabis industry intellectual property.

## Contents

### Scripts
- `enhanced_patent_downloader.py` - Comprehensive cannabis patent downloader
- `requirements.txt` - Python dependencies for the downloader

### Directories
- `corpus/` - Downloaded patent documents in text and JSON format
- `vectorstore/` - FAISS indices and embeddings for patent search
- `knowledge_base/` - Structured patent knowledge files
- `models/` - Local AI models for patent analysis
- `datasets/` - Training and evaluation datasets

## Usage

### Download Cannabis Patents

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the patent downloader:
```bash
python enhanced_patent_downloader.py
```

This will download all US patents related to cannabis from:
- Google Patents (patents.google.com)
- USPTO PatFT Database (patft.uspto.gov)
- USPTO Patent API (developer.uspto.gov)

### Output

Patents are saved in multiple formats:
- Individual JSON files: `cannabis_patent_[number].json`
- Training text files: `cannabis_patent_[number].txt`
- Corpus file: `cannabis_patents_corpus.jsonl`
- Summary report: `download_summary.json`
- CSV index: `cannabis_patents_index.csv`

## Data Sources

All patent data is sourced from public databases:
- **Google Patents**: Public search interface, no API key required
- **USPTO PatFT**: Official US patent database, free access
- **USPTO API**: Public endpoints for patent metadata

## Search Terms

The downloader searches for patents using comprehensive cannabis-related terms:
- Basic: cannabis, marijuana, hemp, cannabinoid
- Compounds: THC, CBD, CBG, CBN, terpenes
- Processes: extraction, cultivation, processing
- Products: oils, edibles, topicals, vaporizers
- Medical: therapeutic applications, treatments
- Testing: analysis, quality control, potency

## Classification Codes

Patents are also searched using relevant classification codes:
- A61K31/05 - Cannabis compounds
- A61K36/185 - Cannabis preparations
- C07D311/58 - Cannabinoid chemistry
- A23L33/105 - Cannabis food products
- And more...

## Git LFS

Large files are tracked with Git LFS including:
- Vector store indices
- Model files
- Large dataset files
- Patent document collections

## Legal Notice

All patent data is sourced from public databases and used for research and analysis purposes under fair use provisions.