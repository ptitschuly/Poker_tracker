#!/usr/bin/env python3
"""
Poker Tracker Test Runner Agent

This agent automatically discovers and runs tests for the Poker Tracker application.
It provides comprehensive test execution with detailed reporting and error analysis.

Usage:
    python test_runner_agent.py [options]

Options:
    --verbose, -v    : Enable verbose output
    --quiet, -q      : Suppress output except for failures
    --module, -m     : Run tests for specific module only
    --list, -l       : List all available tests without running them
    --help, -h       : Show this help message
"""

import unittest
import sys
import os
import argparse
import time
from io import StringIO
import traceback


class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class with colored output"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.use_colors = hasattr(stream, 'isatty') and stream.isatty()
        self.verbosity = verbosity
    
    def _color_text(self, text, color_code):
        """Apply color to text if colors are supported"""
        if self.use_colors:
            return f"\033[{color_code}m{text}\033[0m"
        return text
    
    def addSuccess(self, test):
        super().addSuccess(test)
        if self.verbosity > 1:
            self.stream.write(self._color_text("✓ ", "32"))  # Green checkmark
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write(self._color_text("✗ ", "31"))  # Red X
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write(self._color_text("✗ ", "31"))  # Red X
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write(self._color_text("⊘ ", "33"))  # Yellow skip


class TestRunnerAgent:
    """Main test runner agent class"""
    
    def __init__(self):
        self.test_modules = [
            'test_poker_logic',
            'test_poker_calculations', 
            'test_history_parsing'
        ]
        self.start_time = None
        self.end_time = None
        
    def discover_tests(self, module_filter=None):
        """Discover all test cases"""
        loader = unittest.TestLoader()
        test_suite = unittest.TestSuite()
        
        modules_to_test = self.test_modules
        if module_filter:
            modules_to_test = [m for m in self.test_modules if module_filter in m]
        
        discovered_modules = []
        
        for module_name in modules_to_test:
            try:
                # Import the test module
                module = __import__(module_name)
                
                # Load tests from the module
                module_suite = loader.loadTestsFromModule(module)
                test_suite.addTest(module_suite)
                discovered_modules.append(module_name)
                
            except ImportError as e:
                print(f"Warning: Could not import test module '{module_name}': {e}")
            except Exception as e:
                print(f"Error loading tests from '{module_name}': {e}")
        
        return test_suite, discovered_modules
    
    def list_tests(self, module_filter=None):
        """List all available tests without running them"""
        print("🔍 Discovering available tests...\n")
        
        test_suite, discovered_modules = self.discover_tests(module_filter)
        
        print(f"📋 Found {len(discovered_modules)} test modules:")
        
        for module_name in discovered_modules:
            print(f"\n📁 {module_name}")
            
            try:
                module = __import__(module_name)
                loader = unittest.TestLoader()
                module_suite = loader.loadTestsFromModule(module)
                
                test_count = 0
                for test_group in module_suite:
                    for test_case in test_group:
                        test_count += 1
                        test_name = test_case._testMethodName
                        class_name = test_case.__class__.__name__
                        print(f"  └── {class_name}.{test_name}")
                
                print(f"  📊 Total tests in module: {test_count}")
                
            except Exception as e:
                print(f"  ❌ Error analyzing module: {e}")
    
    def run_tests(self, verbosity=2, module_filter=None, quiet=False):
        """Run all discovered tests"""
        self.start_time = time.time()
        
        if not quiet:
            print("🚀 Starting Poker Tracker Test Suite")
            print("=" * 50)
        
        # Discover tests
        test_suite, discovered_modules = self.discover_tests(module_filter)
        
        if not quiet:
            print(f"📦 Running tests from {len(discovered_modules)} modules")
            if module_filter:
                print(f"🔍 Filter: {module_filter}")
            print()
        
        # Create custom test runner
        stream = sys.stdout if not quiet else StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=verbosity if not quiet else 0,
            resultclass=ColoredTextTestResult,
            buffer=True
        )
        
        # Run the tests
        result = runner.run(test_suite)
        
        self.end_time = time.time()
        
        # Print summary
        self._print_summary(result, discovered_modules, quiet)
        
        return result.wasSuccessful()
    
    def _print_summary(self, result, discovered_modules, quiet):
        """Print test execution summary"""
        duration = self.end_time - self.start_time
        
        if quiet and (result.errors or result.failures):
            # In quiet mode, only show errors/failures
            if result.errors:
                print("\n❌ ERRORS:")
                for test, error in result.errors:
                    print(f"\n{test}: {error}")
            
            if result.failures:
                print("\n❌ FAILURES:")
                for test, failure in result.failures:
                    print(f"\n{test}: {failure}")
        
        if not quiet or result.errors or result.failures:
            print("\n" + "=" * 50)
            print("📊 TEST SUMMARY")
            print("=" * 50)
            
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"📁 Modules: {len(discovered_modules)}")
            print(f"🧪 Tests run: {result.testsRun}")
            
            if result.wasSuccessful():
                print("✅ Result: ALL TESTS PASSED")
            else:
                print("❌ Result: SOME TESTS FAILED")
                
            if result.failures:
                print(f"💥 Failures: {len(result.failures)}")
                
            if result.errors:
                print(f"🚨 Errors: {len(result.errors)}")
                
            if result.skipped:
                print(f"⊘  Skipped: {len(result.skipped)}")
        
        # Always show final status
        if result.wasSuccessful():
            status = "✅ SUCCESS" if not quiet else "PASS"
        else:
            status = "❌ FAILURE" if not quiet else "FAIL"
        
        print(f"\n🏁 Final Status: {status}")
    
    def run_with_coverage_analysis(self):
        """Run tests with basic coverage analysis"""
        print("🔍 Running tests with coverage analysis...\n")
        
        # Import all main modules to check coverage
        main_modules = [
            'poker_logic',
            'poker_calculations',
            'poker_ev_gui',
            'recapitulatif_tournoi',
            'recapitulatif_cash_game',
            'recapitulatif_expresso'
        ]
        
        covered_modules = []
        uncovered_modules = []
        
        for module_name in main_modules:
            try:
                __import__(module_name)
                covered_modules.append(module_name)
            except ImportError:
                uncovered_modules.append(module_name)
        
        print(f"📦 Modules available for testing: {len(covered_modules)}")
        print(f"⚠️  Modules not available: {len(uncovered_modules)}")
        
        if uncovered_modules:
            print(f"   Missing: {', '.join(uncovered_modules)}")
        
        print()
        
        # Run normal tests
        return self.run_tests()


def main():
    """Main entry point for the test runner agent"""
    parser = argparse.ArgumentParser(
        description="Poker Tracker Test Runner Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true', 
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--quiet', '-q', 
        action='store_true', 
        help='Suppress output except for failures'
    )
    
    parser.add_argument(
        '--module', '-m', 
        type=str, 
        help='Run tests for specific module only'
    )
    
    parser.add_argument(
        '--list', '-l', 
        action='store_true', 
        help='List all available tests without running them'
    )
    
    parser.add_argument(
        '--coverage', '-c', 
        action='store_true', 
        help='Run with coverage analysis'
    )
    
    args = parser.parse_args()
    
    # Create test runner agent
    agent = TestRunnerAgent()
    
    try:
        if args.list:
            agent.list_tests(args.module)
            return 0
        
        # Determine verbosity
        verbosity = 1  # Default
        if args.verbose:
            verbosity = 2
        elif args.quiet:
            verbosity = 0
        
        # Run tests
        if args.coverage:
            success = agent.run_with_coverage_analysis()
        else:
            success = agent.run_tests(verbosity, args.module, args.quiet)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)