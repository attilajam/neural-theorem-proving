import csv

def write_dict_to_csv(data: list[dict], filename: str = 'output.csv'):
    if not data:
        print("The input data list is empty. No CSV file will be created.")
        return

    fieldnames = data[0].keys()

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row_dict in data:
                writer.writerow(row_dict)
        print(f"Successfully wrote data to {filename}")
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
