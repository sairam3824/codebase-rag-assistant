"""Chat engine with conversation history."""
from typing import List, Dict, Optional
from openai import OpenAI
import os
from .prompts import get_prompt_for_query, SYSTEM_PROMPT


class ChatEngine:
    """Manage conversations with context."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.history: List[Dict[str, str]] = []
    
    def chat(self, query: str, context: str, stream: bool = False) -> str:
        """
        Send a query with context and get response.
        
        Args:
            query: User question
            context: Retrieved code context
            stream: Whether to stream the response
        
        Returns:
            Assistant response
        """
        # Select appropriate system prompt
        system_prompt = get_prompt_for_query(query)
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history (last 5 exchanges)
        messages.extend(self.history[-10:])
        
        # Add current query with context
        user_message = f"Context from codebase:\n\n{context}\n\nQuestion: {query}"
        messages.append({"role": "user", "content": user_message})
        
        # Get response
        if stream:
            return self._stream_response(messages, query)
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update history
            self.history.append({"role": "user", "content": query})
            self.history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
    
    def _stream_response(self, messages: List[Dict], query: str):
        """Stream response token by token."""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        # Update history after streaming
        self.history.append({"role": "user", "content": query})
        self.history.append({"role": "assistant", "content": full_response})
    
    def clear_history(self):
        """Clear conversation history."""
        self.history = []
