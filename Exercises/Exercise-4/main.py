import json
import os
import csv
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def identify_json_files(current_dir: str):
    json_files = []

    # crawl through current directory for every folder and file to find json
    for dir, folders, files in os.walk(current_dir):
        for file in files:
            if file.endswith(".json"):
                full_path = os.path.join(dir, file)
                json_files.append(full_path)
    
    print(f"Found {len(json_files)} json files")

    return json_files

# uses two pass approach, flattens JSON record by identifying max record for each key, write header to csv file
# then go through file again to flat data, store in memory, and push to CSV file buffer

# this function is used to go through each item in json file and flatten it
# recursively go through each value within the file, crawling through each key and value
def flatten_file(current_value, parent_key = '', sep = '_'):
    file_dict = {}

    # get the keys
    if isinstance(current_value, dict):
        for k, v in current_value.items():
            if parent_key: # if parent key exist
                new_key = parent_key + sep + k
            else:
                new_key = k

            file_dict.update(flatten_file(v, new_key, sep=sep))

    # get the values
    elif isinstance(current_value, list):
        for i, v in enumerate(current_value):
            if parent_key:
                new_key = parent_key + sep + str(i)
            else:
                new_key = str(i)

            file_dict.update(flatten_file(v, new_key, sep=sep))
    else:
        file_dict[parent_key] = current_value
    
    return file_dict

def convert_json_to_csv(json_file: str):
    csv_file = json_file.replace(".json", ".csv")

    # get all headers through first pass at json file
    headers = set()

    with open(json_file, "r", encoding="utf-8") as f:
        records = json.load(f)

        # wrap records in list type so the for record in records can step through key and value pairs instead of just returning key values
        if isinstance(records, dict):
            records = [records]

        for record in records:
            flattened = flatten_file(record)
            headers.update(flattened.keys())

    headers_list = sorted(list(headers))
    print(headers_list)

    # write each row by passing through each record in json file again and write directly to csv file
    with open(csv_file, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers_list)

        writer.writeheader()

        for record in records:
            flattened_record = flatten_file(record)
            writer.writerow(flattened_record)
    
    print(f"CSV saved - {csv_file}")

def convert_json_to_csv_pandas(json_file:str):
    csv_file = json_file.replace(".json", ".csv")

    df = pd.read_json(json_file)

    flat_df = pd.json_normalize(df.to_dict(orient='records'))

    flat_df.to_csv(csv_file, index=False)


def main():
    # your code here
    json_files = identify_json_files(CURRENT_DIR)
    if len(json_files) > 0:
        for json_file in json_files:
            convert_json_to_csv(json_file)
            # convert_json_to_csv_pandas(json_file)

    pass


if __name__ == "__main__":
    main()

# Generally, your script should do the following ...
# 1. Crawl the `data` directory with `Python` and identify all the `json` files. // save into list
# 2. Load all the `json` files. // create function to flat json file and save to csv file within same folder // repeat same action for all list
# 3. Flatten out the `json` data structure.
# 4. Write the results to a `csv` file, one for one with the json file, including the header names.
