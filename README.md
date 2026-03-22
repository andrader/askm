# askm: Agent Skills Manager

`askm` is a tool for managing agent skills. It helps maintain a collection of specialized agents and their associated instructions.

## Project Structure

- `skills/`: The core collection of skill definitions and their metadata.
- `src/askm/`: The Python-based management CLI (Agent Skills Manager).


## Installation

You can run `askm` directly or install it as a tool using `uv`:

```bash
# Run without installing
uvx git+https://github.com/andrader/askm --help

# Install as a global tool
uv tool install git+https://github.com/andrader/askm
askm --help

# Or with pip
pip install git+https://github.com/andrader/askm
askm --help
```

## Getting Started

```bash
# Example command (to be implemented)
askm --help
```


## Contributing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/andrader/askm
cd askm

# Install dependencies
uv sync
```




