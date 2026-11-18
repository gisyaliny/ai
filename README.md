# AI Tools Learning Handbook

A Jupyter Book repository documenting learning materials on AI tools and technologies, including:

- Vibe Coding
- RAG (Retrieval-Augmented Generation)
- MCP (Model Context Protocol)
- Skills
- And more...

## Setup

This repository uses the Sphinx-based Jupyter Book 1.x toolchain. Use Python 3.10–3.12 for the documented build; the requirements keep Jupyter Book below version 2 because this book uses `_config.yml` and `_toc.yml`.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Building the Book

To build the Jupyter Book:

```bash
jupyter-book build .
```

To build and serve locally:

```bash
jupyter-book build . && jupyter-book serve .
```

## Structure

- `docs/` - Contains all the notebook content organized by topic
- `_config.yml` - Jupyter Book configuration
- `_toc.yml` - Table of contents structure
- `index.md` - Landing page

## Mac Studio Coding Agent Workshop

Start at [the workshop guide](docs/workshops/macstudio-agent/index.md). Eight labs reconstruct a VS Code coding assistant with a Mac-hosted model. Each lab includes acceptance evidence, copyable code, and a quiz; the guide links a downloadable source bundle.
