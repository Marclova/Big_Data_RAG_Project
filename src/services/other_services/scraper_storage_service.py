import os
import requests
from tempfile import NamedTemporaryFile
from unstructured.partition.auto import partition


# DEFAULT_PATH = "downloadedFiles"

#TODO use Llama_Index library to perform text extraction and partitioning (documentation: https://developers.llamaindex.ai/python/examples/low_level/vector_store)
#TODO(improvement): If possible, find a way so that the webScraper can gather name, pages and authors from the file
def extract_and_partition_text_from_url(url: str) -> list[str]:
    """
    Method to extract and partition text for any textual file (ex. TXT, PDF).
    The method will create and delete a temporary file.
    Parameters:
        url (str): The url to download the file from and then extract the text.
    Returns:
        list[str]: The list of partitioned chunk of text from the file.
    """
    # a stream has not been used due to compatibility issues with binary an structured files
    try:
    # download file as a request
        r: requests.Response = requests.get(url, stream=False)
        r.raise_for_status()

        # save physically a temporary file
        tmp_path: str = None
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(r.content)
            tmp_path = tmp.name

        # text extraction (auto-format detection and default partitioning with 'libmagic')
        elements = partition(filename=tmp_path)
    finally:
        # Ensure temporary file is deleted
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return [el.text for el in elements if el.text]


# def download_file(file_url: str, file_extension: str, file_name: str = "appendFile", folder_path: str = DEFAULT_PATH) -> str:
#     """
#     Downloads a file from the url into a determined folder.

#     Parameters:
#         file_url (str): The url used to download the file.
#         file_extension (str): The expected extension of the file to download.
#         file_name (str, default="appendFile"): The name to assign to the file once downloaded.
#         folder_path (str, default=DEFAULT_PATH): The local path wherein to put the downloaded file.
    
#     Returns:
#         str: The file path, which is the concatenation of folder_path + file_name + file_extension. 
#             None if the file has not been downloaded correctly.
#     """
#     file_extension = RD_operator.normalize_extension(file_extension)
    
#     try:
#         if not os.path.exists(folder_path):
#             os.makedirs(folder_path)

#         file_path = os.path.join(folder_path, file_name + file_extension)

#         response = requests.get(file_url, stream=True)
#         response.raise_for_status()

#         with open(file_path, 'wb') as file:
#             for chunk in response.iter_content(chunk_size=8192):
#                 file.write(chunk)

#         if not os.path.exists(file_path):
#             raise FileNotFoundError
#     except Exception as e:
#         print(f"ERROR: {file_name}{file_extension} has not been downloaded.\nError log: {e}")
#         return None
#     return file_path


# def delete_file(file_path: str) -> int:
#     """
#     Deletes the given file.
#     Parameters:
#         file_path (str): The path of the file to delete.
#     Returns:
#         int: '1' if the file has been eliminated correctly\n
#             '0' if the file didn't exist in first place\n
#             '-1' if an error occurred
#     """
#     if not(os.path.exists(file_path)):
#         return 0
#     try:
#         os.remove(file_path)
#     except Exception as e:
#         print(f"Error occurred while deleting file: {e}")
#         return -1
#     return 1 if not(os.path.exists(file_path)) else -1


# def get_file_content(file_path: str) -> str:
#     """
#     Retrieves the content of the given file.
#     Parameters:
#         file_path (str): The path of the file to read.
#     Returns:
#         str: The content of the file.
#     """
#     doc = pymupdf.open(file_path)
#     text = "\n".join([page.get_textbox("text") for page in doc])
#     return text
