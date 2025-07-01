# Legal Document Index Generator

A comprehensive tool for extracting and indexing legal concepts, terms, and rules from PDF documents. This tool automatically identifies statutes, case citations, legal phrases, and professional terminology to create organized, searchable indexes.

## Features

- **Comprehensive Term Recognition**: Identifies NY statutes, CPLR/CPL rules, case citations, and legal terminology
- **Multiple Output Formats**: Generate indexes in text or JSON format
- **Categorized Results**: Terms organized by legal categories (civil procedure, contracts, torts, etc.)
- **Cross-References**: Automatic linking of related legal concepts
- **Statistics**: Detailed analysis of indexed content
- **Docker Support**: Containerized deployment for consistent results
- **GitHub Actions Integration**: Automated processing workflows

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
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
# Clone the repository
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
2. **Clone repository**: `git clone <your-repo-url>`
3. **Build image**: `docker build -t legal-indexer .`

### Local Python Installation

1. **Prerequisites**: Python 3.8+ installed
2. **Clone repository**: `git clone <your-repo-url>`
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
python legal_index.py document.pdf
```

#### Advanced Options
```bash
# JSON output with statistics
python legal_index.py document.pdf -o index.json --json --stats

# Text output without subcategories
python legal_index.py document.pdf -o simple_index.txt --no-subcategories

# Show help
python legal_index.py --help
```

## Environment Variables (Docker)

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_PDF` | `/input/document.pdf` | Path to input PDF file |
| `OUTPUT_FILE` | `/output/legal_index.txt` | Path for output index file |
| `OUTPUT_FORMAT` | `text` | Output format: `text` or `json` |
| `INCLUDE_SUBCATEGORIES` | `true` | Include detailed subcategories |
| `SHOW_STATS` | `true` | Display indexing statistics |
| `CUSTOM_TERMS_FILE` | _(empty)_ | Path to custom terms JSON file |

## Command Line Options (Local)

| Option | Description |
|--------|-------------|
| `input_pdf` | Path to input PDF file (required) |
| `-o, --output` | Output file path (default: `legal_index.txt`) |
| `-j, --json` | Save output as JSON format |
| `--no-subcategories` | Exclude subcategory details |
| `--stats` | Print indexing statistics |

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

Summary Judgment
  Civil Procedure: 5, 12, 18
  All references: 5, 12, 18, 22

New York Civil Practice Law § 3212
  Ny Statutes: 12
  All references: 12
```

### JSON Format
```json
{
  "Summary Judgment": {
    "civil_procedure": [5, 12, 18],
    "all_references": [5, 12, 18, 22]
  },
  "New York Civil Practice Law § 3212": {
    "ny_statutes": [12],
    "all_references": [12]
  }
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
