# ADR 003: Python Version Choice (3.11)

Date: 2025-08-16  
Status: Proposed  

## Context
The project requires a stable, performant, and widely-supported Python version.  
Key considerations include:  
- Compatibility with AI/ML libraries (FastAPI, NumPy, Pandas, Prophet).  
- Smooth setup on Apple Silicon (M4 MacBook Pro).  
- Long-term maintainability and minimal dependency friction.  

Python 3.12 offers some incremental performance improvements, but ecosystem support (especially for data science / forecasting packages) sometimes lags. Python 3.11 provides both strong performance and broad, proven compatibility today.  

## Decision
Use **Python 3.11** as the default runtime for local development and CI/CD.  

## Options Considered
- **Python 3.11 (Chosen)**  
  - Pros: Stable, wide support across libraries, strong performance.  
  - Cons: Will eventually need upgrading.  
- **Python 3.12**  
  - Pros: Slightly faster, latest features.  
  - Cons: Some packages may not yet have wheels or complete support; possible install pain.  
- **Stay on older LTS (e.g., 3.10)**  
  - Pros: Very safe, but becoming outdated.  
  - Cons: Misses performance gains; may be dropped by libraries sooner.  

## Consequences
- Development and CI pinned to Python 3.11.  
- Later upgrade path: test 3.12+ via a CI matrix before adopting as default.  
- Reduces “dependency doesn’t install” friction for the MVP phase.  

## Follow-ups
- Add `pyenv` instructions to `README.md` for consistent local versioning.  
- Update CI workflow to explicitly use `3.11`.  
- Create a future ADR when upgrading beyond 3.11 is viable.  
