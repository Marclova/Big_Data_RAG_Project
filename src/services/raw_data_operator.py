def normalize_extension(given_string: str) -> str:
    """
    Normalizes the given string to have a leading dot (.) if it doesn't already have one.
    Parameters:
        given_string (str): The string to normalize.
    Returns:
        str: The normalized string with a leading dot.
    """
    if given_string[0] != ".":
        return ("." + given_string)
    else:
        return given_string


def cluster_text(text_to_cluster: str) -> list[str]:
    """
    Extracts the text from a text file (ex. txt or PDF) and clusters it into a list of strings.
    Parameters:
        filePath (str): The path to the file.
    Returns:
        list[str]: The clustered text extracted from the file.
    """
    # doc = pymupdf.open(filePath)    
    # text = "\n".join([page.get_textbox("text") for page in doc])
    # text = scraper_storage_service.get_file_content(filePath)

    # return cluster_text_for_embeddings(text_to_cluster)
    return text_to_cluster.split("\n") #TODO(unscheduled) consider a more effective solution


# def cluster_text_for_embeddings(text: str) -> list[str]:
#     return text.split("\n")


#TODO(testing)
def increase_09az_id_with_carry(id: str) -> str:
    """
    Increases the given id, which is supposed to be a string of digits and lowercase letters, by one.\n
    The applied increment includes a carry operation, so that the id is always a string of digits and lowercase letters.\n
    The returned id may be longer than the original one by one character, which in that case will be completely filled with '0's.\n
    This method may also work with ids containing characters that are not digits nor lowercase letters,
    but in that case only the last character will have more probability to be normalized into the expected range.
    Parameters:
        id (str): The id to increase.
    Returns:
        str: The increased id.
    """
    #0 = 48     9 = 57     a = 97     z = 122
    
    index = len(id) - 1
    carry = True

    while not(carry) or index >= 0:
        #increase the current character
        id[index] = chr(ord(id[index]) + 1)

        #check if carry is needed
    if (id[index] > '9' and id[index] < 'a') or id[index] > 'z':
        id[index] = '0'
        index -= 1
    else:
        carry = False
    
    if carry: #if carry is True, we need to add a new character to apply the carry
        id = '0' + id
    return id