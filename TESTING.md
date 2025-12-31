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

## Test Coverage

The test runner automatically includes coverage reporting. Coverage helps you see which parts of your code are tested.

### Running Tests with Coverage

Coverage is automatically included when you run `run_tests.py`:

```bash
# Run all tests with coverage
python run_tests.py

# Run unit tests with coverage
python run_tests.py unit

# Run integration tests with coverage
python run_tests.py integration
```

### Viewing Coverage Reports

After tests run, you'll see:
- **Terminal summary**: Coverage percentages shown in the terminal output
- **Missing lines**: Lines without coverage are listed (with `--cov-report=term-missing`)
- **HTML report**: A detailed HTML report is generated in `htmlcov/index.html`

To view the HTML report:
1. Open `htmlcov/index.html` in your web browser
2. Browse through your code to see which lines are covered (green) and which aren't (red)
3. Click on files to see detailed line-by-line coverage

### What Coverage Shows

- **Coverage percentage**: The percentage of code lines executed by tests
- **Missing lines**: Specific lines that weren't executed during tests
- **Branch coverage**: Whether all code paths (if/else branches) were tested

### Installing Coverage Tools

Coverage tools are included in `requirements.txt`. Install them with:

```bash
pip install -r requirements.txt
```

This installs `pytest-cov`, which provides the coverage functionality.

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

# Run with coverage (coverage is already included in run_tests.py)
python -m pytest app/test --cov=app --cov-report=html --cov-report=term --cov-report=term-missing
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

