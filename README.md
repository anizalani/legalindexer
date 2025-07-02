# Legal Document Index Generator

A comprehensive tool for extracting and indexing legal concepts, terms, and rules from PDF documents. This tool automatically identifies statutes, case citations, legal phrases, and professional terminology to create organized, searchable indexes.

## Features

- **Comprehensive Term Recognition**: Identifies NY statutes, CPLR/CPL rules, case citations, and legal terminology
- **Multiple Output Formats**: Generate indexes in text, JSON, PDF, DOCX, CSV, XML, and Markdown formats.
- **Categorized Results**: Terms organized by legal categories (civil procedure, contracts, torts, etc.)
- **Cross-References**: Automatic linking of related legal concepts
- **Statistics**: Detailed analysis of indexed content
- **Docker Support**: Containerized deployment for consistent results
- **GitHub Actions Integration**: Automated processing workflows

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/anizalani/legalindexer.git
cd legal-index-generator

# Build the Docker image
docker build -t legal-indexer .

# Run with your PDF
docker run --rm \
  -v "/path/to/your/pdfs:/input:ro" \
  -v "/path/to/output:/output" \
  -e INPUT_PDF="/input/your-document.pdf" \
  -e OUTPUT_FILE="/output/legal_index.txt" \
  legal-indexer
```

### Option 2: Local Installation

```bash
# Clone the sitory
git clone anizalani/legalindexer
cd legal-index-generator

# Install dependencies
pip install PyMuPDF PyPDF2

# Run the indexer
python legal_index.py document.pdf -o legal_index.txt --stats
```

## Installation

### Docker Installation

1. **Prerequisites**: Docker installed on your system
2. **Clone repository**: `git clone https://github.com/anizalani/legalindexer.git
3. **Build image**: `docker build -t legal-indexer .`

### Local Python Installation

1. **Prerequisites**: Python 3.8+ installed
2. **Clone repository**: `git clone https://github.com/anizalani/legalindexer.git
3. **Install dependencies**: `pip install -r requirements.txt`

## Usage

### Docker Usage

#### Basic Usage
```bash
docker run --rm \
  -v "/path/to/pdfs:/input:ro" \
  -v "/path/to/output:/output" \
  -e INPUT_PDF="/input/document.pdf" \
  legal-indexer
```

#### Advanced Configuration
```bash
docker run --rm \
  -v "/path/to/pdfs:/input:ro" \
  -v "/path/to/output:/output" \
  -e INPUT_PDF="/input/contract.pdf" \
  -e OUTPUT_FILE="/output/contract_index.json" \
  -e OUTPUT_FORMAT="json" \
  -e INCLUDE_SUBCATEGORIES="true" \
  -e SHOW_STATS="true" \
  legal-indexer
```

#### Using Docker Compose
```bash
# Place your PDF in ./input/document.pdf
docker-compose up
```

### Local Python Usage

#### Basic Usage
```bash
legal-indexer document.pdf
```

#### Advanced Options
```bash
# PDF output with statistics
legal-indexer document.pdf -o index.pdf --stats

# Text output without subcategories
legal-indexer document.pdf -o simple_index.txt --no-subcategories

# Show help
legal-indexer --help
```

## Environment Variables (Docker)

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_PDF` | `/input/document.pdf` | Path to input PDF file |
| `OUTPUT_FILE` | `/output/legal_index.txt` | Path for output index file. The format is determined by the file extension. |
| `OUTPUT_FORMAT` |_(empty)_| Force a specific output format (e.g., `pdf`, `docx`). Overrides file extension detection. |
| `INCLUDE_SUBCATEGORIES` | `true` | Include detailed subcategories |
| `SHOW_STATS` | `true` | Display indexing statistics |
| `PAGE_OFFSET` | `0` | Offset for page numbers (e.g., -4 if content starts on page 5) |
| `CUSTOM_TERMS_FILE` | _(empty)_ | Path to custom terms JSON file |

## Command Line Options (Local)

| Option | Description |
|--------|-------------|
| `input_pdf` | Path to input PDF file (required) |
| `-o, --output` | Output file path (default: `legal_index.txt`). The format is determined by the file extension. |
| `-f, --format` | Force a specific output format (e.g., `pdf`, `docx`). Overrides file extension detection. |
| `--no-subcategories` | Exclude subcategory details |
| `--stats` | Print indexing statistics |
| `--page-offset` | Offset for page numbers (e.g., -4 if content starts on page 5) |

## GitHub Actions Integration

This repository includes a GitHub Actions workflow for automated processing:

1. **Go to Actions tab** in your GitHub repository
2. **Select "Legal Document Index Generator"**
3. **Click "Run workflow"**
4. **Configure inputs**:
   - Input PDF path
   - Output filename
   - Format (text/json)
   - Include subcategories
   - Show statistics
   - Output directory

The workflow will process your PDF and save the index as a downloadable artifact.

## Recognized Legal Content

### Statutes & Rules
- New York statutes (various codes)
- CPLR (Civil Practice Law & Rules)
- CPL (Criminal Procedure Law)
- Generic rules and regulations

### Case Citations
- Traditional case format: *Plaintiff v. Defendant*
- Federal case citations
- Court decisions and appeals

### Legal Terminology Categories
- **Civil Procedure**: jurisdiction, service of process, summary judgment
- **Contracts**: consideration, breach, unconscionability
- **Torts**: negligence, strict liability, damages
- **Evidence**: hearsay, privilege, authentication
- **Family Law**: custody, support, equitable distribution
- **Criminal Law**: mens rea, defenses, sentencing
- **Professional Responsibility**: attorney-client privilege, conflicts
- **Business Law**: corporations, partnerships, fiduciary duties
- **Real Property**: landlord-tenant, mortgages, easements
- **Estates & Trusts**: wills, probate, estate planning

## Output Examples

### Text Format
```
COMPREHENSIVE LEGAL INDEX
==================================================

CASE LAW REFERENCES
--------------------------------------------------
People v. Smith: 10, 25
Jones v. ABC Corp.: 15

STATUTORY REFERENCES
--------------------------------------------------
CPLR § 3212: 5, 12, 18
New York Judiciary Law § 487: 22

INDEX BY SUBJECT
--------------------------------------------------

-- Civil Procedure --
Summary Judgment: 5, 12, 18

-- Torts --
Negligence: 30, 45

ALPHABETICAL INDEX
--------------------------------------------------
CPLR § 3212: 5, 12, 18
Jones v. ABC Corp.: 15
Negligence: 30, 45
New York Judiciary Law § 487: 22
People v. Smith: 10, 25
Summary Judgment: 5, 12, 18
```

### JSON Format
```json
{
  "case_law_references": {
    "People v. Smith": [10, 25],
    "Jones v. ABC Corp.": [15]
  },
  "statutory_references": {
    "CPLR § 3212": [5, 12, 18],
    "New York Judiciary Law § 487": [22]
  },
  "subject_matter_index": {
    "Summary Judgment": {
      "civil_procedure": [5, 12, 18],
      "all_references": [5, 12, 18]
    },
    "Negligence": {
      "torts": [30, 45],
      "all_references": [30, 45]
    }
  },
  "_cross_references": {}
}
```

## File Structure

```
legal-index-generator/
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Local testing configuration
├── entrypoint.sh             # Docker entrypoint script
├── legal_index.py            # Main indexer script
├── requirements.txt          # Python dependencies
├── .github/
│   └── workflows/
│       └── legal-index.yml   # GitHub Actions workflow
├── input/                    # Place PDFs here (for Docker Compose)
├── output/                   # Generated indexes appear here
└── README.md                 # This file
```

## Customization

### Adding Custom Legal Terms

Create a JSON file with custom terms:

```json
{
  "custom_category": [
    "custom term 1",
    "custom term 2"
  ],
  "specialized_law": [
    "patent law term",
    "trademark concept"
  ]
}
```

Use with Docker:
```bash
-e CUSTOM_TERMS_FILE="/input/custom_terms.json"
```

### Modifying Recognition Patterns

Edit the `LEGAL_PATTERNS` and `PHRASE_PATTERNS` dictionaries in `legal_index.py` to customize term recognition.

## Troubleshooting

### Common Issues

**PDF Not Found**
- Verify the PDF path is correct
- Check file permissions
- Ensure the file is mounted correctly in Docker

**Empty Output**
- Check if PDF contains searchable text
- Try a different PDF extraction method
- Verify PDF is not image-only

**Permission Errors**
- Check output directory permissions
- Use appropriate volume mounting in Docker

### Docker Troubleshooting

```bash
# Check if container is running
docker ps

# View container logs
docker logs <container-id>

# Debug inside container
docker run -it --rm legal-indexer /bin/bash
```

### Performance Tips

- For large PDFs, increase Docker memory limits
- Use SSD storage for faster I/O
- Process multiple PDFs in parallel using separate containers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

Legal Document Index Generator    Copyright (C) 2025  Aniz Alani

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

## Support

For issues and questions:
- Create an issue in this repository
- Check existing issues for solutions
- Review the troubleshooting section

## Changelog

### v1.0.0
- Initial release
- Docker support
- GitHub Actions integration
- Comprehensive legal term recognition
