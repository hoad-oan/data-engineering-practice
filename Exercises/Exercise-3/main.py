import boto3
import os
import zipfile
import gzip
import shutil
import io

s3 = boto3.resource('s3')
my_bucket = s3.Bucket("commoncrawl")
s3_key = "crawl-data/CC-MAIN-2022-05/wet.paths.gz"
# crawl-data/CC-MAIN-2022-05/segments/1642320299852.23/wet/CC-MAIN-20220116093137-20220116123137-00000.warc.wet.gz

def download_from_s3(s3_key: str):

    # setup local file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(script_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True)

    s3_local_file = os.path.basename(s3_key)
    s3_local_file_path = os.path.join(download_dir, s3_local_file)

    extracted_file = s3_local_file.replace(".gz",".txt")
    extracted_file_path = os.path.join(download_dir, extracted_file)

    # download file
    # s3 = boto3.resource('s3')
    print(f"Extracting from s3_key: {s3_key}")
    my_bucket.download_file(s3_key, s3_local_file_path)

    # extract file
    with gzip.open(s3_local_file_path, "rb") as f_in:
        with open(extracted_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return extracted_file_path

def download_from_s3_from_memory(s3_key: str):
    # download into RAM by getting object
    print(f"Extracting file from memory: {os.path.basename(s3_key)}")
    s3_object = my_bucket.Object(s3_key)
    compressed_data = s3_object.get()['Body'].read()

    # virtual file in RAM
    compressed_stream = io.BytesIO(compressed_data)

    # unzip from memory
    with gzip.GzipFile(fileobj=compressed_stream, mode="rb") as gz:
        # stream data in memory instead of unzipping all to memory
        uri = gz.readline().decode("utf-8").strip()
    
    return uri


def read_from_file(extracted_file, line_to_read):

    with open(extracted_file, "r", encoding="utf-8") as file:
        if line_to_read == -1:
            for line in file:
                print(file.readline().strip()) # print all in file. strip to remove /n
        else:
            for line in range(line_to_read):
                line = file.readline()
                print(line.strip()) # print all in file. strip to remove /n

                if not line:
                    break
                uri = line # return for the line that you want
            return uri
            
    return None

def main():
    # # Option 1: load file to hard drive
    # extracted_file_path = download_from_s3(s3_key)
    # print(f"Extracted file: {extracted_file_path}")

    # # download uri from first line of extracted file
    # uri = read_from_file(extracted_file_path, 1)
    # uri_file_path = download_from_s3(uri)

    # read_from_file(uri_file_path, -1)

    # Option 2: load file to memory
    uri = download_from_s3_from_memory(s3_key)
    print(f"Extracted this uri: {uri}")
    uri_data = download_from_s3_from_memory(uri)
    print(f"Extracted this uri: {uri_data}")


if __name__ == "__main__":
    main()


# 1. `boto3` download the file from s3 located at bucket `commoncrawl` and key `crawl-data/CC-MAIN-2022-05/wet.paths.gz`
# 2. Extract and open this file with Python (hint, it's just text).
# 3. Pull the `uri` from the first line of this file.
# 4. Again, download the that `uri` file from `s3` using `boto3` again.
# 5. Print each line, iterate to stdout/command line/terminal.
