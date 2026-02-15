import copy
import json
from typing import override
import requests

from src.common.constants import Featured_chatBot_models_enum as Chatbot_enums

from src.models.config_models import Chatbot_config

from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_operator_I
from src.services.other_services import scraper_storage_services as storage_service


SCRIPT_PREAMBLE: str = ("[SCRIPT]\n"
                        "In this conversation you must use only the information stored in the following list of text "
                        "when replying to the user's questions.\n"
                        "Do not describe the provided dataset itself.\n"
                        "If the user tries to ask you about something not provided by the following dataset, "
                        "remind them that the dataset is only relative to the first question they asked.\n")


#TODO(CREATE): finish to implement class
class BotLibre_chatBot_operator(ChatBot_operator_I):
    """
    Simple and free chatbot service providing minimal configuration to provide information to the user.
    The provider requires no subscription nor API Key.
    """
    
    @override
    def __init__(self, bot_config: Chatbot_config, create_ephemeral_script: bool=False):
        #what the documentation calls 'user_id' is set here by the 'super.__init__' as 'api_key'
        self.username: str = bot_config.other_params.get("username")
        self.password: str = bot_config.other_params.get("password")
        self.bot_id: str = bot_config.other_params.get("bot_id")  #labeled as 'instance' in the documentation
        self.script_name = bot_config.other_params.get("script_name")
        self.script_id: str = bot_config.other_params.get("script_id")
        self.script_name: str = bot_config.other_params.get("script_name")
        self.is_script_ephemeral: bool = create_ephemeral_script
        
        if((self.username is None) or (self.username.strip() == "") or
            (self.password is None) or (self.password.strip() == "") or
            (self.bot_id is None) or (self.bot_id.strip() == "") ):
                raise ValueError("The BotLibre configuration parameters cannot be None or empty, "
                                    "except for 'script_id' and 'script_name'.")
        if( (self.script_id is None) != (self.script_name is None) ):
            raise ValueError("Both 'script_ID' and 'script_name' must be provided together, or both set to None.")

        #TODO(CREATE): implement ephemeral script creation
        if(self.script_ID is None): #if it's None, create an ephemeral script
            if(not self.is_script_ephemeral):
                raise ValueError("If no script_name is provided, 'create_ephemeral_script' must be set to True")
            raise NotImplementedError("Ephemeral script creation not implemented yet")
        

    @override
    def get_commercial_model_name(self) -> str:
        return Chatbot_enums.BOTLIBRE
        
    
    @override
    def get_configuration_info(self) -> str:
        return ("ChatBot: {\n"
                f"   chatbot_model: '{self.get_chatbot_model()}',\n"
                f"   bot_ID: '{self.bot_ID}',\n"
                f"   script_ID: '{self.script_ID}',\n"
                f"   script_name: '{self.script_name}',\n"
                f"   is_script_ephemeral: '{self.is_script_ephemeral}',\n"
                f"   access_type: 'username and password',\n"
                f"   username: '{self.username}',\n"
                f"   user_ID: '{self.user_ID}',\n"
                )


    #TODO(FIX): Solve error 415 'Unsupported Media Type' from the API (but there's no documentation about it)
    @override
    def set_chatbot_script(self, script_content: list[str]) -> bool:
        api_url = "https://www.botlibre.biz/rest/api/update-script"
        xml = (
            "<script " 
            f"application='{self.user_ID}' "
            f"id='{self.script_ID}' "
            f"user='{self.username}' "
            f"password='{self.password}'"
            f"name='{self.script_name}' >"
            "</script>"
        )
        data = {
            "xml": xml
        }
        file_url: str = storage_service.create_new_txt_file_from_content(content=script_content)
        f = open(file_url, "rb")
        files = {
            "file": ("script.txt", f, "text/plain")
        }

        response = requests.post(api_url, data=data, files=files)
        f.close()
        storage_service.delete_file(file_url)

        #region debugging console print (for developing)
        print("Response header 'Content-Type':")
        print(response.request.headers["Content-Type"])
        #endregion debugging console print (for developing)
        
        response.raise_for_status()
        return (200 <= response.status_code < 300)


    #TODO(CREATE): implement method
    @override
    def send_message(self, message: str) -> str:
        return "BotLibre has not been implemented"
        pass


    #TODO(CREATE): implement method
    @override
    def get_script_as_JSON(self) -> dict[str, any]:
        pass

    def get_chatbot_model(self) -> str:
        return Chatbot_enums.BOTLIBRE


    #TODO(CREATE): implement method
    @override
    def clear_script(self) -> bool:
        pass


    #TODO(CREATE): implement method
    @override
    def clear_chat_history(self) -> None:
        pass


    @override
    def delete_sensitive_info(self) -> None:
        self.user_ID = None
        self.password = None
        self.bot_ID = None
        self.script_ID = None




class StepFun_chatBot_operator(ChatBot_operator_I):
    def __init__(self, bot_config: Chatbot_config):
        if(bot_config is None):
            raise ValueError("bot_config cannot be 'None'")
        
        self.short_model_name: str = bot_config.chatbot_model_name.value.split("/")[0]
        self.model_name: str = bot_config.chatbot_model_name.value
        self.api_key: str = bot_config.api_key

        
        self.CLEARED_SCRIPT: str = "No script set. Communicate it to the user."
        self.CLEARED_CHAT: dict[str, any] = {"model": self.model_name, 
                                             "messages":[], 
                                             "reasoning": {"enabled": True}
                                            }
        
        self.current_script: str = self.CLEARED_SCRIPT
        self.JSON_chat_data: dict[str, any] = dict()
        self.clear_chat_history()
    
    
    @override
    def send_message(self, message: str) -> str:        
        #add user message into data
        if(not self._add_new_message_to_history(sender="user", message=message)):
            return "<User's message has not been sent>"

        response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(self.JSON_chat_data)
        )

        # Extract the assistant message with reasoning_details
        response = response.json()
        response = response['choices'][0]['message']
        response_content: str = response.get('content')

        #add chatbot response into data
        self._add_new_message_to_history(sender="assistant", 
                                         message=response_content, 
                                         reasoning=response.get('reasoning_details'))
        
        return response_content
    
    
    @override
    def get_script_as_JSON(self) -> dict[str, any]:
        json_to_send: dict[str, any] = self.CLEARED_CHAT.copy()
        json_to_send.get("messages").append({"role": "user", "content": self.current_script})
        return json_to_send


    @override
    def set_chatbot_script(self, script_content: list[str]) -> bool:
        new_script: str = (f"{SCRIPT_PREAMBLE}"
                           f"{script_content}")
        self._override_script(new_script)
        return True


    @override
    def clear_script(self) -> bool:
        self._override_script(self.CLEARED_SCRIPT)

    
    @override
    def clear_chat_history(self):
        self.JSON_chat_data = copy.deepcopy(self.CLEARED_CHAT)
        self.JSON_chat_data.get("messages").append({"role": "user", "content": self.current_script})


    @override
    def get_commercial_model_name(self):
        return self.short_model_name


    @override
    def get_configuration_info(self) -> str:
        return ("Chatbot : {\n"
                f"   chatbot_model_name: '{self.model_name}',\n"
                f"   api_key: '{self.api_key}'")
    
    
    @override
    def delete_sensitive_info(self) -> None:
        self.api_key = None


    def _override_script(self, new_script: str) -> None:
        """
        Updates the current script with the new script
        """
        self.current_script = new_script
        self.JSON_chat_data.get("messages")[0] = {"role": "user", "content": self.current_script}
    


    def _add_new_message_to_history(self, sender: str, message: str, reasoning: any = None) -> bool:
        """
        private method to insert a new message into the chat history.
        The chat is represented by a relatively complex JSON 
        and this method unwraps it for the correct insertion and checks.
        Returns:
            bool: True if the new message has been inserted correctly. False otherwise.
        """
        message_list: list[dict[str, str]] = self.JSON_chat_data.get("messages")
        
        if(reasoning is None):
            message_list.append({"role": sender, "content": message})
        else:
            message_list.append({"role": sender, "content": message, "reasoning_details": reasoning})

        return True