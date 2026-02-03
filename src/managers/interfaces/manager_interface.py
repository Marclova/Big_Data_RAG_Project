from abc import ABC, abstractmethod


class Manager_I(ABC):
    """
    Interface for all manager in the system.
    Defines methods needed ny the orchestrator to manage the different managers.
    """

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnects the manager from any external resources (e.g., databases, APIs).
        """
        pass