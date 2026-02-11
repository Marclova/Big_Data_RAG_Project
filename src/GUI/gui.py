import logging
import tkinter as tk
from tkinter import (ttk, messagebox)

from src.GUI.log_handler import TkinterLogHandler

from src.controllers.application_controller import Application_controller



class AppGUI:
    def __init__(self, root: tk.Tk, controller: Application_controller):
        self.controller = controller

        self.root = root
        self.root.title("Project GUI")
        self.root.geometry("900x500")

        # layout principale
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._build_log_panel()
        self._build_controls()
        self._setup_logging()



    def _build_log_panel(self):
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(
            frame,
            state="disabled",
            wrap="word"
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text["yscrollcommand"] = scrollbar.set



    def _build_controls(self):
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        ttk.Button(
            frame,
            text="display configurations",
            command=self._display_configurations
        ).pack(fill="x", pady=5)

        ttk.Label(frame).pack(anchor="w")
        ttk.Label(frame).pack(anchor="w")

        ttk.Label(frame, text="Insert vector index to use (leave empty for default):").pack(anchor="w")
        self.manually_selected_index_entry = ttk.Entry(frame)
        self.manually_selected_index_entry.pack(fill="x", pady=5)

        ttk.Label(frame, text="Insert storage collection to use (leave empty for default):").pack(anchor="w")
        self.manually_selected_collection_entry = ttk.Entry(frame)
        self.manually_selected_collection_entry.pack(fill="x", pady=5)

        ttk.Label(frame, text="Insert PDF file local path or web URL").pack(anchor="w")
        self.file_entry = ttk.Entry(frame)
        self.file_entry.pack(fill="x", pady=5)
        self.file_entry.config(state="disabled")

        self.is_source_a_file = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="Insert PDF document instead",
            variable=self.is_source_a_file,
            command=self._switch_file_db_entry
        ).pack(anchor="w", pady=5)

        ttk.Label(frame).pack(anchor="w")
        ttk.Label(frame).pack(anchor="w")

        ttk.Label(frame, text="Write a question:").pack(anchor="w")
        self.message_input_entry = ttk.Entry(frame)
        self.message_input_entry.pack(fill="x", pady=5)

        ttk.Button(
            frame,
            text="get RAW response",
            command=self._send_question_for_RAG_response
        ).pack(fill="x", pady=5)

        ttk.Button(
            frame,
            text="get chatbot response",
            command=self._send_question_for_chatbot_response
        ).pack(fill="x", pady=5)
        
        ttk.Button(
            frame,
            text="ingest documents into vector DB",
            command=self._ingest_documents
        ).pack(fill="x", pady=5)



    def _setup_logging(self):
        handler = TkinterLogHandler(self.log_text)
        handler.setFormatter(
            logging.Formatter(
                "> %(message)s", 
                "%S"
            )
        )
        logging.getLogger().addHandler(handler)



    #region controller -> coordinator methods

    def _display_configurations(self):
        logging.info(self.controller.get_configuration_info())


    def _send_question_for_RAG_response(self):
        question = self.message_input_entry.get()
        if(question == ""):
            return
        logging.info("User: " + question)
        result = self.controller.reply_to_question_raw_response(question, self._get_RAG_index_to_use())
        logging.info("System:\n" + str(result))

    
    def _send_question_for_chatbot_response(self):
        question = self.message_input_entry.get()
        if(question == ""):
            return
        logging.info("User: " + question)
        result = self.controller.reply_to_question(question, self._get_RAG_index_to_use())
        logging.info("System:" + str(result))

        
    def _ingest_documents(self):
        used_source: str = self._get_storage_source_to_use()
        used_index: str = self._get_RAG_index_to_use()
        if(self._confirm_embedding(used_source=used_source, 
                                       concerned_index=used_index)):
            failedChunks: list[str]
            if(self.is_source_a_file.get()):
                logging.info(f"Embedding file '{used_source}' into index '{used_index}'...")
                (_, failedChunks) = self.controller.ingest_documents_from_urls([used_source], used_index)
            else:
                logging.info(f"Embedding all files in collection '{used_source}' into index '{used_index}'...")
                (_, failedChunks) = self.controller.ingest_all_documents_from_storage(used_source, used_index)
            logging.info(f"Embedding terminated with {len(failedChunks)} errors.")

    #endregion controller -> coordinator methods

    #region gui logic methods

    def _get_RAG_index_to_use(self) -> str:
        if(self.manually_selected_index_entry.get()):
            return self.manually_selected_index_entry.get()
        else:
            return self.controller.default_RAG_DB_index_name
        

    def _get_storage_source_to_use(self) -> str:
        if(self.is_source_a_file.get()):
            return self.file_entry.get()
        else:
            if(self.manually_selected_collection_entry.get()):
                return self.manually_selected_collection_entry.get()
            else:
                return self.controller.default_Storage_DB_collection_name


    def _switch_file_db_entry(self):
        if self.is_source_a_file.get():
            self.file_entry.config(state="normal")
            self.manually_selected_collection_entry.config(state="disabled")
        else:
            self.file_entry.config(state="disabled")
            self.manually_selected_collection_entry.config(state="normal")

    
    def _confirm_embedding(self, used_source: str, concerned_index: str) -> bool:
        if(not self.is_source_a_file.get()):
            used_source = self.controller.storage_DB_name + '.' + used_source
        concerned_index = self.controller.rag_DB_name + '.' + concerned_index
        
        confirmed = messagebox.askyesno(
            title="Vector index override warning",
            message=(
                f"This operation will damage the RAG index if source or destination are not correct.\n"
                f"Please verify that the following targets correspond to the expected ones.\n\n"
                f"'{used_source} --> {concerned_index}'\n\n"
                "Do you wish to proceed?"
            ),
            icon="warning"
        )
        return confirmed

    #endregion gui logic methods