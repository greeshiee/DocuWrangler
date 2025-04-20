import os
from openai import AzureOpenAI
import chromadb
from chromadb.config import Settings
import config  # Your configuration file

def initialize_clients():
    # Initialize Azure OpenAI client
    azure_client = AzureOpenAI(
        api_key=config.AZURE_OPENAI_API_KEY,  # From your config file
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,  # From your config file
        api_version="2024-10-21"  # Latest available version as of April 2025
    )
    
    # Initialize ChromaDB client (persistent local storage)
    chroma_client = chromadb.PersistentClient(
        path=config.CHROMA_DB_PATH,  # Path from your config file
        settings=Settings()
    )
    
    return azure_client, chroma_client

