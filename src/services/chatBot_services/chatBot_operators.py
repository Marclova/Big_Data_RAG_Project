import copy
import json
from typing import override
# from urllib import response
# from aiohttp import FormData
import requests

from src.common.constants import Featured_chatBot_models_enum as Chatbot_enums

from src.models.config_models import (BotLibre_chatbot_config, StepFun_chatbot_config)

from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_I
from src.services.other_services import scraper_storage_services as storage_service



#TODO(CREATE): finish to implement class
class BotLibre_chatBot_operator(ChatBot_I):
    """
    Simple and free chatbot service providing minimal configuration to provide information to the user.
    The provider requires no subscription nor API Key.
    """
    
    @override
    def __init__(self, bot_config: BotLibre_chatbot_config, create_ephemeral_script: bool=False):
        self.username: str = bot_config.username
        self.user_ID: str = bot_config.api_key #labeled as 'application' in the documentation
        self.password: str = bot_config.password
        self.bot_ID: str = bot_config.bot_id #labeled as 'instance' in the documentation
        self.script_ID: str = bot_config.script_id #may be None
        self.script_name: str = bot_config.script_name #may be None
        self.is_script_ephemeral: bool = create_ephemeral_script

        #TODO(CREATE): implement ephemeral script creation
        if(self.script_ID is None): #if it's None, create an ephemeral script
            if(not self.is_script_ephemeral):
                raise ValueError("If no script_name is provided, 'create_ephemeral_script' must be set to True")
            raise NotImplementedError("Ephemeral script creation not implemented yet")
        
    
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

    # def get_all_botLibre_bots(self) -> any:
    #     var request = new XMLHttpRequest();
    #     request.open('POST', 'https://www.botlibre.biz/rest/api/get-bots', true);
    #     request.setRequestHeader('Content-Type', 'application/xml');
    #     var xml = "<browse application='3855908076414615606' ></browse>";
    #     request.onreadystatechange = function() {
    #         exampleResult.setValue(request.responseText, -1);
    #     };
    #     request.send(xml);

    # code to set bot script (probably the url is incorrect)
    # xml = f"<script-source application='7860132618576389205' instance='instance-id' id='{self.script_id}' user='{self.username}' password='{self.password}'></script-source>"
    # headers = {'Content-Type': 'application/xml'}
    # response = requests.post('https://www.botlibre.biz/rest/api/up-bot-script', data=xml, headers=headers)
    # return response.text


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




#TODO(CREATE): implement class
class StepFun_chatBot_operator(ChatBot_I):
    #TODO(CREATE): implement method
    @override
    def __init__(self, bot_config: StepFun_chatbot_config):
        if(bot_config is None):
            raise ValueError("bot_config cannot be 'None'")
        
        self.model_short_name: str = bot_config.short_name
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
        not self._add_new_message_to_history(sender="assistant", 
                                             message=response_content, 
                                             reasoning=response.get('reasoning_details'))
        # if(not self._add_new_message_to_history(sender=self.model_name, 
        #                                         message=response.get('content'), 
        #                                         reasoning=response.get('reasoning_details'))):
        #     return "<Chatbot's message has been deleted by the local system due to an unexpected issue>"
        
        return response_content
    
    
    @override
    def get_script_as_JSON(self) -> dict[str, any]:
        json_to_send: dict[str, any] = self.CLEARED_CHAT.copy()
        json_to_send.get("messages").append({"role": "user", "content": self.current_script})
        return json_to_send


    @override
    def set_chatbot_script(self, script_content: list[str]) -> bool:
        new_script: str = ("[SCRIPT]\n"
                           "In this conversation you must use only the information stored in the following list of text "
                           "when replying to the user's questions:\n"
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
        
        # #Make sure that no one talks twice in a raw
        # if(message_list[-1].get("role") == sender):
        #     if(sender == self.model_name):
        #         raise BufferError("The chatbot replied twice")
        #     return False
        
        if(reasoning is None):
            message_list.append({"role": sender, "content": message})
        else:
            message_list.append({"role": sender, "content": message, "reasoning_details": reasoning})

        return True