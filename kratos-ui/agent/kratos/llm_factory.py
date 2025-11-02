from langchain_ollama import ChatOllama

from enum import Enum
from typing import Union, Any
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class ModelProvider(Enum):
    """Enumeration of supported LLM model providers with their configurations."""
    OLLAMA = {
        "provider": "ollama", 
        "api_base": "http://localhost:11434", 
        "default_model": "llama3.2:3b"
    }
    OLLAMA_CLOUD = {
        "provider": "ollama_cloud", 
        "api_base": "https://ollama.com", 
        "default_model": "kimi-k2:1t-cloud"
    }
    OPENAI = {
        "provider": "openai",
        "api_base": "https://api.openai.com/v1",
        "default_model": "gpt-4"
    }
    DEEPSEEK = {
        "provider": "deepseek",
        "api_base": "https://api.deepseek.com/v1",
        "default_model": "deepseek-reasoner"
    }
    OPENROUTER = {
        "provider": "openrouter",
        "api_base": "https://openrouter.ai/api/v1",
        "default_model": "anthropic/claude-sonnet-4"
    }
    OTHER = {
        "provider": "other",
        "api_base": None,
        "default_model": None
    }

class LLMFactory:
    """Factory class to create LLM instances based on the specified model provider."""
    
    @staticmethod
    def get_llm_model(model_name: str = None, 
                      model_provider: ModelProvider = ModelProvider.OLLAMA) -> Union[ChatOllama, Any]:
        """Returns an instance of the specified LLM model based on the provider."""
        provider_config = model_provider.value
        
        if model_provider == ModelProvider.OLLAMA:
            # Use provided model_name or fall back to default
            model_to_use = model_name or provider_config["default_model"]
            return ChatOllama(
                model=model_to_use, 
                base_url=provider_config["api_base"]
            )
        elif model_provider == ModelProvider.OLLAMA_CLOUD:
            from langchain_ollama import ChatOllama
            # Use provided model_name or fall back to default
            model_to_use = model_name or provider_config["default_model"]
            api_key = os.getenv("OLLAMA_API_KEY")
            if not api_key:
                raise ValueError("OLLAMA_API_KEY environment variable not set.")
            return ChatOllama(
                model_name=model_to_use,
                api_key=api_key,
                base_url=provider_config["api_base"]
            )
        elif model_provider == ModelProvider.DEEPSEEK:
            from langchain_openai import ChatOpenAI
            # Use provided model_name or fall back to default
            model_to_use = model_name or provider_config["default_model"]
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable not set.")
            return ChatOpenAI(
                model_name=model_to_use,
                openai_api_key=api_key,
                openai_api_base=provider_config["api_base"],
                temperature=0.7, max_completion_tokens=20000
            )
        elif model_provider == ModelProvider.OPENROUTER:
            from langchain_openai import ChatOpenAI
            # Use provided model_name or fall back to default
            model_to_use = model_name or provider_config["default_model"]
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable not set.")
            return ChatOpenAI(
                model_name=model_to_use,
                openai_api_key=api_key,
                openai_api_base=provider_config["api_base"],
                temperature=0.7, max_completion_tokens=20000,
                timeout=300
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider_config['provider']}")