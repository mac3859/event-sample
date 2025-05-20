import pytest      # The pytest testing framework
import subprocess  # For running the command-line script as a subprocess
import json        # Although not strictly needed for these tests, good practice to import if dealing with JSON
import os          # For path manipulation
import sys         # For sys.executable

# Define the path to the script under test relative to the test file.
# This assumes the test file is in 'tests/' and the script is in the parent directory of 'tests/'.
# Adjust this path based on your actual project structure if different.
# Based on your structure example-data/tests/test_tests.py and example-data/patient-event-processor.py
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'patient-event-processor.py')

# Define the path to the directory containing test data files.
# This assumes the 'data/' directory is inside the 'tests/' directory.
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def run_processor(input_file_name):
    """
    Helper function to run the patient-event-processor.py script with a given input file name.
    Constructs the full path to the input file in the DATA_DIR.
    Returns the completed process object from subprocess.run.
    """
    # Construct the full path to the input data file using the DATA_DIR
    full_input_path = os.path.join(DATA_DIR, input_file_name)

    # Check if the script file exists before trying to run it.
    # This is a test setup check to ensure the test environment is correct.
    if not os.path.exists(SCRIPT_PATH):
        pytest.fail(f"Script not found at {SCRIPT_PATH}")

    # Note: We do NOT check if the input_file_name exists here in the helper,
    # because some tests (like test_file_not_found) are specifically designed
    # to pass a non-existent file path to the script under test.
    # The script under test is responsible for handling FileNotFoundError.

    # Run the script using subprocess.run.
    # sys.executable ensures we use the same Python interpreter that's running pytest.
    # capture_output=True captures stdout and stderr.
    # text=True decodes stdout and stderr as text.
    # check=False prevents raising CalledProcessError on non-zero exit codes,
    # allowing us to assert on the return code and stderr for error cases.
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, full_input_path],
        capture_output=True,
        text=True,
        check=False
    )
    return result

# --- Test Cases ---

def test_valid_example_data():
    """Tests the script with the exact example data from the task."""
    input_file = "valid_example.json"
    # Define the expected output exactly as specified, including the newline characters.
    expected_output = (
        "Olivia: d9392a98.tiff, f796f432.tiff\n"
        "Sophie: ccd803fd.tiff\n"
    )
    expected_exit_code = 0 # Expect a successful exit code (0)

    # Run the script with the valid example data
    result = run_processor(input_file)

    # Assertions:
    # 1. Check the exit code is as expected.
    assert result.returncode == expected_exit_code, f"Expected exit code {expected_exit_code}, got {result.returncode}. Stderr: {result.stderr}"
    # 2. Check the standard output matches the expected output exactly.
    assert result.stdout == expected_output, f"Expected stdout:\n---\n{expected_output}\n---\nActual stdout:\n---\n{result.stdout}\n---"
    # 3. Check that there is no output on standard error for a successful run.
    assert result.stderr == "", f"Expected empty stderr, got: {result.stderr}"


def test_file_not_found():
    """Tests handling of a non-existent input file."""
    input_file = "non_existent_file.json" # A file name that does not exist in tests/data/
    expected_exit_code = 1 # Expect a non-zero exit code for an error
    # Define parts of the expected error message string.
    # This makes the assertion less brittle to the exact formatting of the path in the error message.
    expected_stderr_part1 = "Error: Input file"
    expected_stderr_part2 = "not found"

    # Run the script with the non-existent file path.
    # The run_processor helper passes this path to the script.
    result = run_processor(input_file)

    # Assertions:
    # 1. Check the exit code is as expected.
    assert result.returncode == expected_exit_code, f"Expected exit code {expected_exit_code}, got {result.returncode}. Stdout: {result.stdout}"
    # 2. Check that standard error contains the expected parts of the error message.
    assert expected_stderr_part1 in result.stderr, f"Expected stderr to contain '{expected_stderr_part1}', got: {result.stderr}"
    assert expected_stderr_part2 in result.stderr, f"Expected stderr to contain '{expected_stderr_part2}', got: {result.stderr}"
    # 3. Check that there is no output on standard output for an error case.
    assert result.stdout == "", f"Expected empty stdout, got: {result.stdout}"


def test_invalid_json_format():
    """Tests handling of an input file with invalid JSON syntax."""
    input_file = "invalid_json.json" # This file must exist in tests/data/ and contain malformed JSON
    expected_exit_code = 1 # Expect a non-zero exit code for an error
    # Define the expected error message substring for JSON decoding errors.
    expected_stderr_substring = "Error: Invalid JSON"

    # Run the script with the invalid JSON file.
    result = run_processor(input_file)

    # Assertions:
    # 1. Check the exit code is as expected.
    assert result.returncode == expected_exit_code, f"Expected exit code {expected_exit_code}, got {result.returncode}. Stdout: {result.stdout}"
    # 2. Check that standard error contains the expected substring for a JSON error.
    assert expected_stderr_substring in result.stderr, f"Expected stderr to contain '{expected_stderr_substring}', got: {result.stderr}"
    # 3. Check that there is no output on standard output for an error case.
    assert result.stdout == "", f"Expected empty stdout, got: {result.stdout}"


# Add more test functions for other scenarios identified in the 10/10 test plan.
# Remember to create the corresponding JSON files in the tests/data/ directory
# for each new test case that requires a specific input file.

# Example of a test for a file with only PatientCreated events (no slides)
# def test_only_patient_created_events():
#     """Tests a file with only PatientCreated events (no slides)."""
#     input_file = "only_created.json" # File with only PatientCreated events
#     expected_output = "" # No output expected because no slides are attached
#     expected_exit_code = 0 # Should still exit successfully
#
#     result = run_processor(input_file)
#
#     assert result.returncode == expected_exit_code
#     assert result.stdout == expected_output
#     assert result.stderr == "" # Expect no errors

# Example of a test for a slide event before a create event
# def test_slide_before_create():
#    """Tests a file where a slide event occurs before the create event."""
#    input_file = "slide_before_create.json" # File with slide event then create event
#    # Assuming the script correctly links the name when the create event arrives
#    expected_output = "Patient Name: file.tiff\n"
#    expected_exit_code = 0
#
#    result = run_processor(input_file)
#
#    assert result.returncode == expected_exit_code
#    assert result.stdout == expected_output
#    assert result.stderr == "" # Expect no errors

# Remember to create 'tests/data/only_created.json' and 'tests/data/slide_before_create.json'
# with appropriate JSON content for these tests to pass.
