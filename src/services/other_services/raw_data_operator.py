


def normalize_extension(given_string: str) -> str:
    """
    Normalizes the given string to have a leading dot (.) if it doesn't already have one.
    Parameters:
        given_string (str): The string to normalize.
    Returns:
        str: The normalized string with a leading dot.
    """
    if(given_string is None or len(given_string) == 0):
        raise ValueError("The given string is None or empty.")

    if given_string[0] != ".":
        return ("." + given_string)
    else:
        return given_string
    

def normalize_folder_path(given_string: str) -> str:
    """
    Normalizes the given folder path to have a trailing slash (/) if it doesn't already have one.
    Parameters:
        given_string (str): The folder path to normalize.
    Returns:
        str: The normalized folder path with a trailing slash.
    """
    if(given_string is None or len(given_string) == 0):
        raise ValueError("The given string is None or empty.")

    if given_string[-1] != "/":
        return (given_string + "/")
    else:
        return given_string


# def cluster_text(text_to_cluster: str) -> list[str]:
#     """
#     Extracts the text from a text file (ex. txt or PDF) and clusters it into a list of strings.
#     Parameters:
#         filePath (str): The path to the file.
#     Returns:
#         list[str]: The clustered text extracted from the file.
#     """
#     return text_to_cluster.split("\n")


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
    if (id == None or len(id) == 0):
        raise ValueError("The given id is None or empty.")

    CHAR_0 = ord('0') #48
    CHAR_9 = ord('9') #57
    CHAR_a = ord('a') #97
    CHAR_z = ord('z') #122
    
    bytearray_id = bytearray(id, 'utf-8')
    index = len(bytearray_id) - 1
    carry = True

    #increase the character at the current index by one ASCII value and move to the previous index as long as carry is needed
    while carry and index >= 0:
        carry = False
        append_val = bytearray_id[index]
        
        #carry case, recursively increase the previous character
        if append_val >= CHAR_z:
            bytearray_id[index] = CHAR_0
            carry = True
            index -= 1
        #skip to 'a' case
        elif append_val >= CHAR_9 and append_val < CHAR_a:
            bytearray_id[index] = CHAR_a
        #skip to '0' case
        elif append_val < CHAR_0:
            bytearray_id[index] = CHAR_0
        #normal case
        else:
            bytearray_id[index] += 1
    
    id = bytearray_id.decode('utf-8')
    #add a new '0' at the beginning if carry is still needed
    if carry:
        id = '0' + id

    return id
