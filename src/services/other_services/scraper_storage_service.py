import os
import pymupdf
import requests

import src.services.raw_data_operator as RD_operator


DEFAULT_PATH = "downloadedFiles"


def download_file(file_url: str, file_extension: str, file_name: str = "appendFile", folder_path: str = DEFAULT_PATH) -> str:
    """
    Downloads a file from the url into a determined folder.

    Parameters:
        file_url (str): The url used to download the file.
        file_extension (str): The expected extension of the file to download.
        file_name (str, default="appendFile"): The name to assign to the file once downloaded.
        folder_path (str, default=DEFAULT_PATH): The local path wherein to put the downloaded file.
    
    Returns:
        str: The file path, which is the concatenation of folder_path + file_name + file_extension. 
            None if the file has not been downloaded correctly.
    """
    file_extension = RD_operator.normalize_extension(file_extension)
    
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, file_name + file_extension)

        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        if not os.path.exists(file_path):
            raise FileNotFoundError
    except Exception as e:
        print(f"ERROR: {file_name}{file_extension} has not been downloaded.\nError log: {e}")  # TODO(unscheduled) Implement proper logging method
        return None
    return file_path


def delete_file(file_path: str) -> int:
    """
    Deletes the given file.
    Parameters:
        file_path (str): The path of the file to delete.
    Returns:
        int: '1' if the file has been eliminated correctly\n
            '0' if the file didn't exist in first place\n
            '-1' if an error occurred
    """
    if not(os.path.exists(file_path)):
        return 0
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error occurred while deleting file: {e}")
        return -1
    return 1 if not(os.path.exists(file_path)) else -1

def get_file_content(file_path: str) -> str:
    """
    Retrieves the content of the given file.
    Parameters:
        file_path (str): The path of the file to read.
    Returns:
        str: The content of the file.
    """
    doc = pymupdf.open(file_path)
    text = "\n".join([page.get_textbox("text") for page in doc])
    return text