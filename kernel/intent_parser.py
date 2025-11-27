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
            "browse",
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
            
            # Normalize LLM response
            if "intent" in intent and "action" not in intent:
                intent["action"] = intent["intent"]
            
            if "action" not in intent:
                return {"action": "unknown", "reason": "Missing 'action' field"}
            
            # Normalize params
            if "params" not in intent:
                # If params are missing, assume the rest of the dict are params
                intent["params"] = {k: v for k, v in intent.items() if k not in ["action", "intent"]}

            # Map specific LLM hallucinations to correct params
            if "filename" in intent["params"] and "path" not in intent["params"]:
                intent["params"]["path"] = intent["params"]["filename"]
            if "file_content" in intent["params"] and "content" not in intent["params"]:
                intent["params"]["content"] = intent["params"]["file_content"]
            if "website" in intent["params"] and "url" not in intent["params"]:
                intent["params"]["url"] = intent["params"]["website"]

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
        
        # If no code blocks, try to find the JSON object manually
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx:end_idx+1]
            
        return "{}" # Fallback
