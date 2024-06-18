import json
import argparse

def remove_entries(file_path, num_entries_to_remove):
    try:
        # Read the existing data from the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Check if the data is a list
        if isinstance(data, list):
            # Remove the specified number of entries
            data = data[:-num_entries_to_remove] if len(data) > num_entries_to_remove else []

            # Write the updated data back to the JSON file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        else:
            print("The JSON data is not a list.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Remove the last N entries from a JSON list.')
    parser.add_argument('file_path', type=str, help='Path to the JSON file')
    parser.add_argument('num_entries_to_remove', type=int, help='Number of entries to remove from the end of the list')

    args = parser.parse_args()

    # Call the function with command line arguments
    remove_entries(args.file_path, args.num_entries_to_remove)

if __name__ == "__main__":
    main()
