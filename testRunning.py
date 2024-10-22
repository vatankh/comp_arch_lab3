import string

import pytest
import yaml
import tempfile
import os
import contextlib
import io
import json

import translator
import machine


# Custom function to load the golden test cases manually
def load_golden_tests(test_directory="tests/"):
    test_files = [f for f in os.listdir(test_directory) if f.endswith("_test.yml")]
    tests = []
    for test_file in test_files:
        with open(os.path.join(test_directory, test_file), 'r') as f:
            tests.append(yaml.safe_load(f))
    return tests


# Helper function to remove the 'term' field from machine code instructions
def remove_terms(machine_code):
    return [{key: value for key, value in instr.items() if key != 'term'} for instr in machine_code]


# Helper function to filter out cache-related log messages
def filter_cache_messages(output):
    return "\n".join([line for line in output.splitlines() if
                      not line.startswith("Write-Through to cache") and not line.startswith("OrderedDict") and not line.startswith(
                          "cache is full delete least used") and not line.startswith("cache miss")])


# Helper function to normalize outputs by stripping extra spaces and normalizing newlines
def normalize_output(output):
    # Strip leading/trailing spaces from each line and join them into a single string
    printable = set(string.printable)
    return "".join([char for char in output if char in printable]).strip()

# Parametrize the test to load all test cases
@pytest.mark.parametrize("golden", load_golden_tests())
def test_golden(golden):
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Setup paths for source, input stream, and target machine code files
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, golden["name"] + "_machine.json")

        # Write the source code (assembly) to a temporary file
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["input"]["source"])

        # Write the input stream (user input) to a temporary file
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["input_stream"]["content"])

        # Step 1: Run the translator to generate machine code
        translator.main(source, target)

        # Read the generated machine code and compare it with the expected machine code
        with open(target, "r", encoding="utf-8") as file:
            generated_code = json.loads(file.read())  # Parse the JSON output to match the structure

        # Remove the 'term' field from the generated machine code before comparing
        generated_code_without_terms = remove_terms(generated_code)

        # Assert that the generated code matches the expected machine code
        assert generated_code_without_terms == golden[
            "expected_machine_code"], "Machine code does not match expected output."

        # Step 2: Run the machine simulation and capture the output
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            machine.main(target, input_stream)
            simulation_output = stdout.getvalue().replace("\x00", "")

        # Filter out cache-related log messages
        filtered_output = filter_cache_messages(simulation_output)

        # Normalize both expected and actual outputs before comparison
        normalized_filtered_output = normalize_output(filtered_output)
        normalized_expected_output = normalize_output(golden["expected_output"])

        # Assert that the filtered and normalized simulation output matches the expected output
        assert normalized_filtered_output == normalized_expected_output, f"Simulation output does not match expected output. \nActual:\n{normalized_filtered_output}\nExpected:\n{normalized_expected_output}"

        # Step 3: Check the processor log
        with open("machine/logs/processor.txt", "r", encoding="utf-8") as log_file:
            processor_log = log_file.read()
            assert processor_log == golden["expected_log"], "Processor log does not match expected output."
