
import unittest
import sys

def run_tests():
    # Discover and load tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)

    # Run tests
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    # Return exit code based on success
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    run_tests()
    

            