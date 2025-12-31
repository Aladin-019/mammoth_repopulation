# Testing Guide

This document describes how to run tests for the Mammoth Repopulation Simulator.

## Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Only Unit Tests
```bash
python run_tests.py unit
```

### Run Only Integration Tests
```bash
python run_tests.py integration
```

### Run Tests with Verbose Output
```bash
python run_tests.py -v
```

### Run Specific Tests
```bash
# Run tests matching a pattern
python run_tests.py -k test_mammoth

# Run a specific test file
python -m pytest app/test/integration/test_mammoth_migration.py -v

# Run a specific test class
python -m pytest app/test/unit/models/Plot/test_PlotGrid_migration.py::TestPlotGridMigration -v
```

## Using pytest Directly

You can also use pytest directly:

```bash
# Run all tests
python -m pytest app/test

# Run with verbose output
python -m pytest app/test -v

# Run and show print statements
python -m pytest app/test -v -s

# Run and stop at first failure
python -m pytest app/test -x

# Run with coverage (if pytest-cov is installed)
python -m pytest app/test --cov=app --cov-report=html
```

## Test Structure

Tests are organized in the `app/test/` directory:

```
app/test/
├── unit/              # Unit tests (fast, isolated tests)
│   ├── models/        # Tests for model classes
│   ├── setup/         # Tests for setup utilities
│   └── data/          # Tests for data loaders
└── integration/       # Integration tests (test multiple components together)
    ├── test_biome_stability.py
    └── test_mammoth_migration.py
```

## Installation

Make sure pytest is installed:

```bash
pip install -r requirements.txt
```

Or install pytest separately:

```bash
pip install pytest
```

## Troubleshooting

### Tests fail with import errors
Make sure you're running tests from the `mammoth_repopulation` directory and that PYTHONPATH is set correctly. The `run_tests.py` script handles this automatically.

### Tests are slow
Integration tests are slower than unit tests. You can run only unit tests for faster feedback:

```bash
python run_tests.py unit
```

### Some tests are skipped
Check if tests are marked with pytest markers. You can run specific markers:

```bash
python -m pytest -m unit
python -m pytest -m integration
```

