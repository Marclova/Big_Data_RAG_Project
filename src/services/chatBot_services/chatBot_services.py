from typing import override
from urllib import response
from aiohttp import FormData
import requests

from src.models.config_models import BotLibre_config
from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_I

import src.services.other_services.scraper_storage_service as storage_service



#TODO(CREATE): implement class
class BotLibre_chatBot_service(ChatBot_I):
    """
    Simple and free chatbot service providing minimal configuration to provide information to the user.
    The provider requires no subscription nor API Key.
    """
    
    @override
    def __init__(self, bot_config: BotLibre_config, create_ephemeral_script: bool=False):
        self.username: str = bot_config.username
        self.password: str = bot_config.password
        self.user_ID: str = bot_config.user_ID #labeled as 'application' in the documentation
        self.bot_ID: str = bot_config.bot_ID #labeled as 'instance' in the documentation
        self.script_ID: str = bot_config.script_ID #may be None
        self.script_name: str = bot_config.script_name #may be None
        self.is_script_ephemeral: bool = create_ephemeral_script

        #TODO(CREATE): implement ephemeral script creation
        if(self.script_ID is None): #if it's None, create an ephemeral script
            if(not self.is_script_ephemeral):
                raise ValueError("If no script_name is provided, 'create_ephemeral_script' must be set to True")
            raise NotImplementedError("Ephemeral script creation not implemented yet")


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
        print("Response header 'Content-Type':")
        print(response.request.headers["Content-Type"])
        response.raise_for_status()
        return (200 <= response.status_code < 300)


    #TODO(CREATE): implement method
    @override
    def send_message(self, message: str) -> str:
        pass


    #TODO(CREATE): implement method
    @override
    def get_script_as_JSON(self) -> dict[str,any]:
        pass


    #TODO(CREATE): implement method
    @override
    def clear_script(self) -> bool:
        pass


#TODO(CREATE): implement class
class OpenAI_chatBot_service(ChatBot_I):
    """
    Simple chatBot service using a powerful provider that can access to further information through the internet 
    and complex thinking and problem solving.
    The provider requires both an API Key (obtained with a subscription on https://platform.openai.com/api-keys), 
    and a small payment for API responses.
    """
    pass
