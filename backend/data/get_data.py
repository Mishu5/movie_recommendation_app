import csv

def get_media_from_tsv(file_path):
    print("Reading file...")
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            rows = [row for row in reader]

        print(rows[0])
        return rows
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist")
    except Exception as e:
        print(f"An error occured: {e}")