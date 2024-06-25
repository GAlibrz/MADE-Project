#!/bin/bash

# Define the paths
LOG_FILE="pipeline_test.log"

# Create necessary directories
mkdir -p ../logs

# Run the Python test script and log the output
echo "Running the Python test script..."
python3 test_pipeline.py > $LOG_FILE 2>&1

# Check the exit status of the test script
if [ $? -eq 0 ]; then
    echo "All tests passed successfully."
else
    echo "Some tests failed. Check the log file for details."
    # exit 1
fi

# exit 0
#;