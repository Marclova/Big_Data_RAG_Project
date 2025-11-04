from abc import ABC, abstractmethod

class DTModel_I(ABC):
    """
    Data Transfer model for storing and retrieving data from a DB
    """

    @abstractmethod
    def generate_JSON_data(self) -> dict[str, any]:
        """
        Returns a dictionary representation of the object for DB storage.
        """
        pass