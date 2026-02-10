from abc import ABC, abstractmethod

from src.models.interfaces.config_interfaces import Configuration_model_I


class Manager_I(ABC):
    """
    Interface for all manager in the system.
    Defines methods needed ny the orchestrator to manage the different managers.
    """
    @abstractmethod
    def get_configuration_info(self) -> str:
        """
        Returns a string summing up all the information (excluding sensible one) used to initialize the manager.
        This method has been meant for debugging or final-user checks.
        Returns:
            str: The summarization of the configuration in the format "operator_name: {parameter_name: value, ...}", 
                    going newline for each parameter and curly bracket.
        """
        pass

    @abstractmethod
    def connect(self, connection_config: Configuration_model_I) -> bool:
        """
        Connects the manager to outer providers or other kind of sources using the given configurations.
            NOTE: This method is meant to be called in a second moment after the class initialization, 
            permitting to retry a failed connection without rebooting the application.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnects the manager from any external resources (e.g., databases, APIs).
        """
        pass