import argparse
import json
import sys
import os # Import os module for path handling

def process_events(file_path: str):
    """
    Processes a JSON file containing patient events and prints a summary
    of patients and their attached slide files.

    Args:
        file_path: The path to the input JSON file.
    """
    # Dictionary to store patient data: {PatientID: {"name": "...", "files": ["...", "..."]}}
    patient_data = {}

    # Construct the full path relative to the current working directory
    # This assumes the script is run from a location where example-data/ exists
    # If the file path is absolute, os.path.join handles it correctly.
    full_file_path = os.path.join(os.getcwd(), file_path)


    try:
        # Open and load the JSON file
        with open(full_file_path, 'r') as f:
            events = json.load(f)

    except FileNotFoundError:
        # Handle case where the input file does not exist
        print(f"Error: Input file '{full_file_path}' not found.", file=sys.stderr)
        sys.exit(1) # Exit with a non-zero status code to indicate an error
    except json.JSONDecodeError:
        # Handle case where the file content is not valid JSON
        print(f"Error: Invalid JSON in file '{full_file_path}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other potential errors during file reading
        print(f"An unexpected error occurred while reading the file: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure the loaded data is a list as expected
    if not isinstance(events, list):
        print(f"Error: Expected JSON array of events, but got {type(events)} from '{full_file_path}'.", file=sys.stderr)
        sys.exit(1)

    # Process each event in the list
    for event in events:
        # Ensure event is a dictionary
        if not isinstance(event, dict):
            print(f"Warning: Skipping non-dictionary event: {event}", file=sys.stderr)
            continue

        event_type = event.get("EventType")
        payload = event.get("Payload")

        # Skip events that don't have a payload dictionary
        if not isinstance(payload, dict):
            # print(f"Warning: Skipping event with missing or invalid payload: {event}", file=sys.stderr)
            continue # Silently skip events without valid payload as they can't contain patient info

        patient_id = payload.get("PatientID")

        # Skip events without a PatientID in the payload
        if not patient_id:
            # print(f"Warning: Skipping event with missing PatientID in payload: {event}", file=sys.stderr)
            continue # Silently skip events without PatientID as they can't be linked

        # Initialize patient entry if it doesn't exist
        if patient_id not in patient_data:
            # Use a placeholder name if PatientCreated hasn't been seen yet
            patient_data[patient_id] = {"name": f"Unknown Patient ({patient_id})", "files": []}

        # Process PatientCreated events
        if event_type == "PatientCreated":
            name = payload.get("Name")
            if name and isinstance(name, str):
                # Update the patient's name. If a slide came first, this corrects the name.
                patient_data[patient_id]["name"] = name
            # else:
                # print(f"Warning: PatientCreated event for {patient_id} missing or invalid 'Name'.", file=sys.stderr)


        # Process PatientCaseSlideAttached events
        elif event_type == "PatientCaseSlideAttached":
            file_name = payload.get("File")
            if file_name and isinstance(file_name, str):
                # Add the file to the patient's list of files
                patient_data[patient_id]["files"].append(file_name)
            # else:
                # print(f"Warning: PatientCaseSlideAttached event for {patient_id} missing or invalid 'File'.", file=sys.stderr)

        # Optionally, add handling for other event types if needed in the future
        # else:
            # print(f"Info: Skipping unknown event type: {event_type}", file=sys.stderr)


    # Output the summary for patients who have attached files
    for patient_id, data in patient_data.items():
        # Only print lines for patients who have at least one file
        if data["files"]:
            print(f"{data['name']}: {', '.join(data['files'])}")

def main():
    """
    Main function to parse command-line arguments and run the event processing.
    """
    parser = argparse.ArgumentParser(
        description="Processes patient event data from a JSON file and outputs a summary of attached slides."
    )
    # Define the command-line argument for the input file
    parser.add_argument(
        "input_file",
        help="Path to the JSON file containing patient events."
    )

    # Parse the arguments provided by the user
    args = parser.parse_args()

    # Call the core processing function with the provided file path
    process_events(args.input_file)

# Standard Python entry point
if __name__ == "__main__":
    main()
