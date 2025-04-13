import os
from urllib import request


DEFAULT_PATH = "downloadedFiles/"

def download_file(file_url: str, file_extension: str, file_name: str = "appendFile", folder_path: str = DEFAULT_PATH) -> str:
    """
    Downloads a file from the url into a determined folder.

    Parameters:
        url (str): The url used to download the file.
        file_extension (str): The expected extension of the file to download.
        file_name (str, default="appendFile"): The name to assign to the file once downloaded.
        folder_path (str, default=DEFAULT_PATH): The local path wherein to put the downloaded file.
    
    Returns:
        str: The file path, which is the concatenation of folder_path + file_name + file_extension
    """
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = folder_path + file_name + file_extension

        request.urlretrieve(file_url, file_path)
        if not( os.path.exists(file_path) ):
            raise FileNotFoundError
    except Exception as e:
        print("ERROR: " + file_name+file_extension +" has not been downloaded.\n error log: " + str(e)) #TODO consider another logging method
        return None
    return file_path

def delete_file(file_path: str) -> int:
    """
    Deletes the given file.

    Returns:
        int: '1' if the file has been eliminated correctly\n
                '0' if the file didn't exist in first place\n
                '-1' if an error occurred
    """
    if not(os.path.exists):
        return 0
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error occurred while deleting file: {e}")
        return -1
    return 1 if not(os.path.exists(file_path)) else -1