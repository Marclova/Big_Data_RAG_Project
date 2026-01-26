from src.common.constants import (Featured_storage_DB_engines_enum as storage_engines)
from src.managers.DB_managers import (Storage_DB_manager, RAG_DB_manager)
from src.managers.embedding_managers import Embedding_manager
from src.models.DB_config_models import (Storage_DB_config, RAG_DB_config)


#TODO(CREATE): implement class
#TODO(FIX): Implement a check to make sure that new embeddings ain't going to create incongruence
#               (mixed vector types in the same collection)
#TODO(TEST): Make sure that any combination of embedding-RAG_DB works
class Coordinator_manager:
    """
    General manager orchestrating other managers in order to permit strict collaboration between managers
        while avoiding horizontal and cyclic dependencies.
    It also permits to check incongruent configurations between managers.
    """
    def __init__(self, storage_conf: Storage_DB_config, rag_conf: RAG_DB_config):
        storage_DB_manager = Storage_DB_manager(storage_conf)
        rag_DB_manager= RAG_DB_manager(rag_conf)

        # embedding_manager= Embedding_mana