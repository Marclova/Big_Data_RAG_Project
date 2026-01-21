import fitz
import os
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PyMuPDFReader



LINE_BREAKERS = {'\n','\b','\r','\v','\x0b','\f','\x0c','\u2028','\u2029'}
STRONG_PUNCTUATIONS = {')','.','!','?'}
STOPWORDS = {"-", ":", ",", ";", "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", 
             "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
             "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", 
             "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", 
             "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", 
             "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", 
             "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", 
             "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", 
             "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", 
             "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
             "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", 
             "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", 
             "yours", "yourself", "yourselves"}



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


def extract_partition_text_and_metadata_from_file(file_path: str, pop_file: bool=True) -> dict[list[str], any]:
    """
    Method to extract and partition text for any textual file (ex. TXT, PDF).
    Parameters:
        file_path (str): The path to the file to extract the text from.
        pop_file (bool): Delete the read file after data extraction.
    Returns:
        dict[str,any]: A dictionary containing:
            - "text_chunks" (list[str]): The list of partitioned chunk of text from the file.
            - "pages_count" (int): The number of pages in the file.
    """
    pages_count: str = str(fitz.open(file_path).page_count)
    loader = PyMuPDFReader()
    documents = loader.load(file_path=file_path)
    node_parser = SentenceSplitter(chunk_size=256)
    nodes = node_parser.get_nodes_from_documents(documents)

    # text_chunk_list: list[str] = list()
    # for node in nodes:
    #     candidate_text_chunk = node.get_content(metadata_mode="none")
    #     text_chunk_list.append[candidate_text_chunk]
    text_chunk_list: list[str] = [node.get_content(metadata_mode="none") for node in nodes]
    text_chunk_list = refine_embedding_textList(text_chunk_list)

    result_dict: dict[str, any] = dict()
    result_dict["text_chunks"] = text_chunk_list
    result_dict["pages_count"] = pages_count

    if(pop_file):
        os.remove(file_path)

    return result_dict


def refine_embedding_textList(text_chunk_list: list[str]) -> list[str]:
    """
    Method to refine an ordered list of text chunks for improved embedding in a RAG system. 
    This function deletes and concatenate the given chunks if needed. 
    Afterwards the same process is executed to single lines.
    WARNING:
        The input text list must represent the complete file in the correct order; otherwise,
        the quality of data collection may decrease from a semantic perspective.
    Parameters:
        candidate_text_chunk (list[str]): The ordered list of text chunks to refine.
    Returns:
        list[str]: The refined list of text chunks.
    """
    append_text: str = ""
    new_text_chunks: list[str] = list()
    for index in range( 0, (len(text_chunk_list)) ): #This iteration works on whole text chunks (single lines operations in the called private function)
        candidate: str = append_text.rstrip(''.join(LINE_BREAKERS)) + text_chunk_list[index].strip()
        append_text = ""

        if(len(candidate) < 150): #May be a title or an isolated string to discard
            if(_ends_with_stopWord(candidate)): #It's the first part of a longer sentence (chain it with the next chunk)
                append_text = candidate + " "
            continue
        elif(_is_heavily_dotted(candidate)): #It's useful and round (no operations)
            pass
        elif(_ends_with_stopWord(candidate)): #It's useful, but the last sentence is chopped (remove last sentence and chain it with the next chunk)
            split_tuple = _pop_last_sentence(candidate)
            candidate = split_tuple[0]
            append_text = split_tuple[1] + " "
        
        candidate = _delete_or_fix_anomalous_lines(candidate) #This function works on single lines
        new_text_chunks.append(candidate)
    return new_text_chunks



def _is_heavily_dotted(string: str) -> bool:
    """
    Checks if the given string ends with a strong pointing. 
    It is assumed that the strings has no trailing whitespaces.
    """
    stripped = string.rstrip(''.join(LINE_BREAKERS))
    return bool(stripped) and stripped[-1] in STRONG_PUNCTUATIONS


def _ends_with_stopWord(string: str) -> bool:
    """
    Checks if the given string ends with a stop word. 
    It is assumed that the strings has no trailing whitespaces.
    """
    tokens = string.split()
    return bool(tokens) and tokens[-1].lower() in STOPWORDS


def _pop_last_sentence(text: str) -> tuple[str, str]:
    """
    Removes the last sentence from the given text.
    The input text does NOT get modified.
    Returns:
        tuple[str,str]: A tuple containing respectively the text [0] and the removed trailing sentence [1].
    """
    tuple_to_return: tuple[str, str] = tuple()
    for index in reversed(range(0, len(text))):
        if((text[index] in STRONG_PUNCTUATIONS) and (text[index] != ')')):
            # tuple_to_return[0] = text[:index+1]
            # tuple_to_return[1] = text[index+1:].lstrip()
            tuple_to_return = tuple((text[:index+1], text[index+1:].lstrip()))
            return tuple_to_return
    #it's a just a single sentence a bit too long
    return tuple((None, text))


def _delete_or_fix_anomalous_lines(text: str) -> str:
    """
    Deletes or fixes lines that are detrimental to dataset quality.

    Processing rules (applied in order):
    - Lines with fewer than 3 words are removed (typically titles or page numbers)
    - Lines ending with strong punctuation are kept as-is (complete sentences)
    - Lines NOT ending with strong punctuation are treated as "chopped" and concatenated 
      with the next line, assuming the next line contains the missing part that was split 
      by a line-breaker character

    Parameters:
        text (str): The text chunk to check and fix (without trailing whitespaces)
    Returns:
        str: The fixed text chunk
    """
    
    new_text: str = ""
    append_line: str = ""
    last_char: str = ''
    for char in text:
        append_line = append_line + char
        if(char not in LINE_BREAKERS): #Keep iterating until a newline is found
            last_char = char
        else: #Begin a chain of controls to the end of the line (the sequence is important)
            if(len(append_line.split(" ")) < 3): #Too short, is a title or a page enumeration (discard)
                pass
            else: #The line is legit...
                new_text = new_text + append_line
                if(last_char not in STRONG_PUNCTUATIONS): #... but chopped
                    new_text = new_text[:-1] + " " #removing the line-breaker character

            append_line = ""
            last_char = ""
    new_text = new_text + append_line #insert remaining append-line
    return new_text