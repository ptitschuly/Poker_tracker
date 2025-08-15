# Test Runner Agent Documentation

## Overview

The Test Runner Agent is an automated testing tool for the Poker Tracker application. It discovers and runs comprehensive tests for all core functionality, providing detailed reporting and error analysis.

## Features

- **Automatic Test Discovery**: Finds all test modules and test cases automatically
- **Comprehensive Coverage**: Tests poker logic, calculations, and history parsing
- **Colored Output**: Visual indicators for test results (✓ pass, ✗ fail, ⊘ skip)
- **Multiple Output Modes**: Verbose, normal, and quiet modes
- **Module Filtering**: Run tests for specific modules only
- **Coverage Analysis**: Basic coverage reporting for available modules
- **Error Reporting**: Detailed error messages and tracebacks

## Usage

### Basic Commands

```bash
# Run all tests with normal output
python test_runner_agent.py

# Run all tests with verbose output (shows each test)
python test_runner_agent.py --verbose

# Run tests in quiet mode (only show final result)
python test_runner_agent.py --quiet

# List all available tests without running them
python test_runner_agent.py --list

# Run tests with coverage analysis
python test_runner_agent.py --coverage
```

### Module-Specific Testing

```bash
# Run only poker logic tests
python test_runner_agent.py --module poker_logic

# Run only calculation tests
python test_runner_agent.py --module calculations

# Run only history parsing tests
python test_runner_agent.py --module history
```

### Command Line Options

- `--verbose, -v`: Enable verbose output showing each test as it runs
- `--quiet, -q`: Suppress output except for failures and final status
- `--module, -m MODULE`: Run tests for specific module only (partial matching)
- `--list, -l`: List all available tests without running them
- `--coverage, -c`: Run with basic coverage analysis
- `--help, -h`: Show help message with all options

## Test Modules

The test suite includes three main test modules:

### 1. test_poker_logic.py
Tests core poker classes and functions:
- `Card` class: Creation, validation, equality, string representation
- `Hand` class: Creation, sorting, validation, equality
- `Player` class: Basic player functionality
- Helper functions: Deck creation, hand parsing, community card parsing

### 2. test_poker_calculations.py  
Tests poker calculation functions:
- Equity calculations using Monte Carlo simulation
- Range parsing (pairs, suited/offsuit hands, plus notation)
- Chip EV calculations
- Complex range strings with multiple components

### 3. test_history_parsing.py
Tests history file parsing modules:
- Tournament result parsing
- Cash game hand parsing  
- Expresso tournament parsing
- File format validation and error handling

## Output Examples

### Normal Mode
```
🚀 Starting Poker Tracker Test Suite
==================================================
📦 Running tests from 3 modules

.......................................
----------------------------------------------------------------------
Ran 39 tests in 0.317s

OK

==================================================
📊 TEST SUMMARY
==================================================
⏱️  Duration: 0.33 seconds
📁 Modules: 3
🧪 Tests run: 39
✅ Result: ALL TESTS PASSED

🏁 Final Status: ✅ SUCCESS
```

### Verbose Mode
Shows each test with visual indicators:
```
✓ test_card_equality (test_poker_logic.TestCard.test_card_equality)
✓ test_card_string_representation (test_poker_logic.TestCard.test_card_string_representation)
✗ test_failing_example (test_example.TestExample.test_failing_example)
⊘ test_skipped_example (test_example.TestExample.test_skipped_example)
```

### Quiet Mode
```
🏁 Final Status: PASS
```

## Exit Codes

- `0`: All tests passed successfully
- `1`: Some tests failed or errors occurred
- `130`: Test execution interrupted by user (Ctrl+C)

## Integration

The test runner can be easily integrated into:
- CI/CD pipelines
- Development workflows
- Pre-commit hooks
- Automated testing schedules

## Adding New Tests

To add new tests:

1. Create a new test file following the pattern `test_[module_name].py`
2. Import the required modules and unittest framework
3. Create test classes inheriting from `unittest.TestCase`
4. Add test methods starting with `test_`
5. The test runner will automatically discover and run new tests

Example test structure:
```python
import unittest
from poker_logic import Card, Hand

class TestNewFeature(unittest.TestCase):
    def test_new_functionality(self):
        """Test new functionality"""
        # Test implementation
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all required dependencies are installed
   ```bash
   pip install matplotlib deuces
   ```

2. **Module Not Found**: Make sure you're running from the correct directory
   ```bash
   cd /path/to/Poker_tracker
   python test_runner_agent.py
   ```

3. **Permission Errors**: Ensure the test runner is executable
   ```bash
   chmod +x test_runner_agent.py
   ```

### Getting Help

Run the help command for detailed usage information:
```bash
python test_runner_agent.py --help
```