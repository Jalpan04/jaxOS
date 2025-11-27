"""
neuro-casio-os/kernel/intent_parser.py

The Intent Parser is the "Semantic Decoder" of the OS.
It translates the probabilistic output of the Neural Kernel (LLM)
into deterministic System Calls.

Research Note:
This module acts as the safety layer, ensuring that the LLM's "hallucinations"
conform to a strict JSON schema before execution.
"""

import json
from typing import Dict, Any, Optional

class IntentParser:
    """
    Validates and routes JSON intents from the Neural Kernel.
    """

    def __init__(self):
        self.valid_actions = {
            "create_file",
            "read_file",
            "delete_file",
            "list_files",
            "system_status",
            "unknown"
        }

    def parse(self, llm_response: str) -> Dict[str, Any]:
        """
        Parses the raw string response from the LLM.
        
        Args:
            llm_response (str): The raw JSON string from the model.
            
        Returns:
            Dict[str, Any]: A structured intent dictionary.
        """
        try:
            # Locate JSON content if wrapped in markdown code blocks
            clean_response = self._extract_json(llm_response)
            intent = json.loads(clean_response)
            
            if "action" not in intent:
                return {"action": "unknown", "reason": "Missing 'action' field"}
            
            if intent["action"] not in self.valid_actions:
                return {"action": "unknown", "reason": f"Invalid action: {intent['action']}"}
                
            return intent
            
        except json.JSONDecodeError:
            return {"action": "unknown", "reason": "Malformed JSON response"}
        except Exception as e:
            return {"action": "unknown", "reason": str(e)}

    def _extract_json(self, text: str) -> str:
        """
        Extracts JSON string from potential Markdown formatting.
        """
        text = text.strip()
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()
        
        # If no code blocks, assume the whole text might be JSON
        if text.startswith("{") and text.endswith("}"):
            return text
            
        return "{}" # Fallback
