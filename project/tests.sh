#!/bin/bash

# Print current working directory
echo "Current working directory:"
pwd

# List contents of current directory
echo "Contents of current directory:"
ls -R

# Define the paths
LOG_FILE="../logs/pipeline_test.log"

# Create necessary directories
mkdir -p ../logs

# Run the Python test script and log the output
echo "Running the Python test script..."
python3 project/test_pipeline.py > $LOG_FILE 2>&1
TEST_EXIT_CODE=$?

# Display the contents of the log file
cat $LOG_FILE

# Check the exit status of the test script
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "All tests passed successfully."
    exit 0
else
    echo "Some tests failed. Check the log file for details."
    exit 1
fi