class DT_model:
    """
    Data Transfer model for storing and retrieving data from a vectorial database.
    Each model represents a text chunk and its associated vector.
    Initially the vector and text are empty, they will be filled after the embedding process.
    """
    def __init__(self, url: str, title: str = "untitled", authors: list[str] = ["unknown"], 
                 id: str = -1, vector: list[float] = list(), text: str = "", embedder_name: str = ""):
        """
        Initializes a data transfer model for storing and retrieving data from a vectorial database.
        """
        if (url == None):
            raise ValueError("URL cannot be None")
        
        title, authors, id, vector, text, embedder_name = self._init_params_normalization(title, authors, id, 
                                                                                          vector, text, embedder_name)
        
        if (vector.__len__() > 0):
            if (text == ""):
                raise ValueError("Text cannot be None if vector is provided")
            if (embedder_name == ""):
                raise ValueError("Embedder cannot be None if vector is provided")

        self.id = id
        self.vector = vector
        self.text = text
        self.url = url
        self.title = title
        self.authors = authors
        self.embedder_name = embedder_name


    def update_vector(self, vector: list[float], text: str, embedder_name: str) -> None:
        """
        Updates the vector, text and embedder of the object.
        """
        if (vector == None or vector.__len__() == 0):
            raise ValueError("Vector cannot be None or empty")
        if (text == None):
            raise ValueError("Text cannot be None")
        if (embedder_name == None):
            raise ValueError("Embedder cannot be None")
        
        self.vector = vector
        self.text = text
        self.embedder_name = embedder_name

    
    def generate_JSON_data(self) -> dict[str, any]:
        """
        Returns a dictionary representation of the object for vectorial database storage.
        """
        return {
            "id": self.id,
            "vector": self.vector,
            "text": self.text,
            "metadata": {
                "title": self.title,
                "authors": self.authors,
                "url": self.url,
                "embedder": self.embedder_name
            }
        }
    
    def _init_params_normalization(self, title: str, authors: list[str], id: int, 
                                   vector: list[float], text: str, embedder_name: str) -> tuple:
        if (title == None or title == ""):
            title = "untitled"
        if (authors == None or authors.__len__() == 0):
            authors = ["unknown"]
        if (id == None):
            id = -1
        if (vector == None):
            vector = list()
        if (text == None):
            text = ""
        if (embedder_name == None):
            embedder_name = ""
        
        return title, authors, id, vector, text, embedder_name