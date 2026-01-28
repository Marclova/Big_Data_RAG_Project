import os
import requests
from tempfile import NamedTemporaryFile
# from unstructured.partition.auto import partition
from pathlib import Path


# from llama_index.core import Document


DEFAULT_PATH = "file_storage"


#TODO(UPDATE): If possible, find a way so that the webScraper can gather authors from the file

def download_file(url: str, download_folder: str = DEFAULT_PATH) -> str:
    """
    Method to download a file from a given URL into a specified folder.
    The file is saved with a name deduced from the URL.
    It will be needed to delete the file manually after usage by calling another method.
    Parameters:
        url (str): The URL to download the file from.
        download_folder (str): The folder where to save the downloaded file.
    Returns:
        str: The path to the downloaded file.
    """
    try:
        if(url is None):
            raise ValueError("The provided url is None")
        
        #download file and save it into a temporary location
        r: requests.Response = requests.get(url, stream=False)
        r.raise_for_status()

        #determine file name from URL
        file_name = url.split("/")[-1]

        # #create download folder (if it doesn't exist)
        # if not os.path.exists(download_folder):
        #     os.makedirs(download_folder)
        # file_path = os.path.join(download_folder, file_name)

        # #save file
        # with open(file_path, 'wb') as file:
        #     file.write(r.content)

        file_path = create_new_txt_file_from_content(content=r.text.splitlines(),
                                                     file_name=file_name, download_folder=download_folder)

        return file_path
    
    except Exception as e:
        raise RuntimeError(f"Error while trying to download file: {e}")
    

def create_new_txt_file_from_content(content: list[str], 
                                     file_name: str = "append_file", download_folder: str = DEFAULT_PATH) -> str:
    """
    Method to create a new text file from the provided content.
    The file is saved into the specified folder with the given name.
    Parameters:
        content (list[str]): The content to write into the text file.
        file_name (str): The name of the text file to create (without extension).
        download_folder (str): The folder where to save the created text file.
    Returns:
        str: The path to the created text file.
    """
    try:
        if(content is None):
            raise ValueError("The provided content is None")
        
        #create download folder (if it doesn't exist)
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        file_path = os.path.join(download_folder, f"{file_name}.txt")

        #save file
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in content:
                file.write(f"{line}\n")
        return file_path
    
    except Exception as e:
        raise RuntimeError(f"Error while trying to create text file: {e}")
    

def delete_file(file_path: str):
    """
    Method to delete a file from the local filesystem.
    Parameters:
        file_path (str): The path to the file to delete.
    """
    try:
        if(file_path is None):
            raise ValueError("The provided file path is None")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"Warning: The file at path '{file_path}' does not exist and cannot be deleted.") #TODO(polishing) Consider another logging method

    except Exception as e:
        raise RuntimeError(f"Error while trying to delete file: {e}")