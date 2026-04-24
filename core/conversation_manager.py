"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/conversation_manager.py
Description: Manages Natural Language Processing (NLP) and context-aware 
             dialogue using the NextToken SDK. Supports multi-model routing 
             via the NextToken Gateway, including OpenRouter models.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import os
import logging
from typing import Optional, Dict, Any
from nexttoken import NextToken
from .events import Events

class ConversationManager:
    """
    Handles LLM-based interactions and system persona management.
    
    This class wraps the NextToken client, providing a simplified interface
    for generating assistant responses while injecting user personality 
    and system context. It supports standard models (GPT, Gemini) and 
    OpenRouter models (prefixed with openrouter/).
    """
    
    def __init__(self, config: Dict[str, Any], memory: Any) -> None:
        """
        Initializes the AI client and loads required credentials.
        
        Args:
            config: System configuration dictionary.
            memory: Instance of MemoryManager for context injection.
        """
        self.config = config
        self.memory = memory
        self.logger = logging.getLogger('ConversationManager')
        
        # Priority: 1. Environment Variable, 2. Config File
        api_key = os.getenv('NEXTTOKEN_API_KEY') or config.get('assistant', {}).get('nexttoken_api_key')
        
        # Load the target model from config. Support OpenRouter by using 'openrouter/' prefix.
        # Example: 'openrouter/google/gemini-2.0-flash-lite:free'
        self.model = config.get('assistant', {}).get('model', 'gpt-4.1-mini')
        
        try:
            if not api_key or 'YOUR_' in api_key:
                self.logger.warning('NextToken API Key missing. Conversational brain will be disabled.')
                self.client = None
            else:
                self.client = NextToken(api_key=api_key)
                self.logger.info(f'NextToken Client initialized. Model: {self.model}')
        except Exception as e:
            self.logger.error(f'Failed to initialize NextToken: {e}')
            self.client = None

    def get_response(self, text: str) -> None:
        """
        Queries the LLM for a response to user input.
        
        Broadcasts the result via the ASSISTANT_RESPONSE event topic.
        
        Args:
            text: Raw user transcription string.
        """
        if not self.client:
            Events.emit(Events.ASSISTANT_RESPONSE, text='Conversational brain is currently offline.')
            return

        try:
            # --- Persona & Context Injection ---
            user_name = self.memory.get('user_name', 'Sir')
            system_prompt = (
                'You are Sentinel, a futuristic JARVIS-style desktop AI assistant. '
                'You are professional, efficient, and slightly witty. '
                f'You are currently assisting {user_name}.'
            )
            
            # --- LLM Execution ---
            # Routing via NextToken Gateway.
            response = self.client.chat.completions.create(
                model=self.model, 
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': text}
                ],
                max_tokens=2000
            )
            
            reply = response.choices[0].message.content
            Events.emit(Events.ASSISTANT_RESPONSE, text=reply)
            
        except Exception as e:
            self.logger.error(f'LLM Error ({self.model}): {e}')
            Events.emit(Events.ASSISTANT_RESPONSE, text='I encountered an error while processing that.')

    def clear_context(self) -> None:
        """Resets conversation history."""
        pass