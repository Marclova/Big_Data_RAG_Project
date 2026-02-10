import os
import tkinter as tk
import yaml

from src.common.constants import Featured_storage_DB_engines_enum as Storage_DB_enums
from src.common.constants import Featured_RAG_DB_engines_enum as RAG_DB_enums
from src.common.constants import Featured_embedding_models_enum as Embedder_enums
from src.common.constants import Featured_chatBot_models_enum as Chatbot_enums

from src.models.config_models import Chatbot_config, Embedder_config, RAG_DB_config, Storage_DB_config

from src.GUI.gui import AppGUI

from src.controllers.application_controller import Application_controller



if __name__=="__main__":

    #region yaml parameters initialization

    # stream = open(os.path.join("src", "app_config_input.yaml"), 'r', encoding="utf-8")
    stream = open("app_config_input.yaml", 'r', encoding="utf-8")
    application_config = yaml.safe_load(stream)
    stream.close()
    
    append_config: dict[str, any] #used as append variable to extract data from the structured yaml file

    used_storage_DB: Storage_DB_enums = Storage_DB_enums.MONGODB
    used_RAG_DB: RAG_DB_enums = RAG_DB_enums.MONGODB
    used_embedder_model_name: Embedder_enums = Embedder_enums.PINECONE_LLAMA_TEXT_EMBED_V2
    used_embedder_APIkey: str = "Pinecone_APIkey"
    used_chatbot: Chatbot_enums = Chatbot_enums.BOTLIBRE

    default_RAG_DB_index_name: str = application_config["storage_collection_name"]
    default_Storage_DB_collection_name: str = application_config["rag_index_name"]

    # initialize storage DB configuration object
    append_config = application_config[used_storage_DB.value]
    storage_config = Storage_DB_config(db_engine = used_storage_DB,
                                       connection_url = append_config.get("db_connection_url"), 
                                       port = append_config.get("port"), 
                                       database_name = append_config.get("db_name"), 
                                       username = append_config.get("username"), 
                                       password = append_config.get("password"))
    
    # initialize RAG DB configuration object
    append_config = application_config[used_RAG_DB.value]
    rag_config = RAG_DB_config(db_engine = used_RAG_DB, 
                               api_key = append_config.get("api_key"), 
                               connection_url = append_config.get("db_connection_url"), 
                               database_name = append_config.get("db_name"))

    # initialize embedder configuration object
    append_config = application_config["embedder_api_keys"]
    embedder_config = Embedder_config(embedder_model_name = used_embedder_model_name, 
                                      embedder_api_key= append_config.get(used_embedder_APIkey))


    append_config = application_config[used_chatbot.value]
    chatbot_config = Chatbot_config(chatbot_model_name= used_chatbot, 
                                    api_key = append_config.get("api_key"), 
                                    other_params = append_config.get("other_params"))

    #endregion yaml parameters initialization

    root = tk.Tk()
    controller = Application_controller(storage_config = storage_config, 
                                        rag_config = rag_config, 
                                        embedder_config = embedder_config, 
                                        chatbot_config = chatbot_config, 
                                        default_RAG_DB_index_name = default_RAG_DB_index_name, 
                                        default_Storage_DB_collection_name = default_Storage_DB_collection_name)
    AppGUI(root, controller)
    root.mainloop()