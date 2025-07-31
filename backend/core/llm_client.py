"""
llm_client.py

LLM Client for Ollama API integration.
Handles communication with local Ollama models for expert decision making.
Supports structured output parsing and error handling.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from core.logging_config import get_logger

logger = get_logger("llm_client")

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.1"):
        """
        Initialize Ollama client.
        
        Args:
            base_url (str): Ollama API base URL
            model_name (str): Name of the model to use
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.api_url = f"{self.base_url}/api/generate"
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate response from Ollama model.
        
        Args:
            prompt (str): User prompt
            system_prompt (str, optional): System prompt
            
        Returns:
            str or None: Model response or None if error
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
                
            logger.debug(f"Sending request to Ollama: {self.api_url}")
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'response' in result:
                logger.debug(f"Received response from {self.model_name}")
                return result['response']
            else:
                logger.error(f"Unexpected response format: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def parse_probabilities(self, response: str) -> Optional[List[float]]:
        """
        Parse probability response from LLM.
        Expected format: [p_buy, p_hold, p_sell] or similar.
        
        Args:
            response (str): Raw LLM response
            
        Returns:
            List[float] or None: Parsed probabilities [buy, hold, sell]
        """
        try:
            # Clean the response
            response = response.strip()
            
            # Try to find array-like patterns
            import re
            
            # Pattern 1: [0.7, 0.2, 0.1] or [0.7,0.2,0.1]
            array_pattern = r'\[([0-9.,\s]+)\]'
            match = re.search(array_pattern, response)
            if match:
                numbers_str = match.group(1)
                numbers = [float(x.strip()) for x in numbers_str.split(',')]
                if len(numbers) == 3:
                    # Normalize to sum to 1.0
                    total = sum(numbers)
                    if total > 0:
                        normalized = [x/total for x in numbers]
                        logger.debug(f"Parsed probabilities: {normalized}")
                        return normalized
            
            # Pattern 2: "buy: 0.7, hold: 0.2, sell: 0.1" or "BUY: 0.7, HOLD: 0.2, SELL: 0.1"
            prob_pattern = r'(?:buy|BUY)[:\s]*([0-9.]+).*?(?:hold|HOLD)[:\s]*([0-9.]+).*?(?:sell|SELL)[:\s]*([0-9.]+)'
            match = re.search(prob_pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                numbers = [float(match.group(1)), float(match.group(2)), float(match.group(3))]
                total = sum(numbers)
                if total > 0:
                    normalized = [x/total for x in numbers]
                    logger.debug(f"Parsed probabilities: {normalized}")
                    return normalized
            
            # Pattern 3: "p_buy = 0.7, p_hold = 0.2, p_sell = 0.1"
            p_pattern = r'p_buy[:\s]*=?\s*([0-9.]+).*?p_hold[:\s]*=?\s*([0-9.]+).*?p_sell[:\s]*=?\s*([0-9.]+)'
            match = re.search(p_pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                numbers = [float(match.group(1)), float(match.group(2)), float(match.group(3))]
                total = sum(numbers)
                if total > 0:
                    normalized = [x/total for x in numbers]
                    logger.debug(f"Parsed probabilities: {normalized}")
                    return normalized
            
            # Pattern 4: Look for three numbers that sum to approximately 1.0
            # This is a fallback for when the LLM gives a detailed explanation
            all_numbers = re.findall(r'\b([0-9]+\.[0-9]+)\b', response)
            if len(all_numbers) >= 3:
                # Try to find three consecutive numbers that sum to ~1.0
                for i in range(len(all_numbers) - 2):
                    try:
                        nums = [float(all_numbers[i]), float(all_numbers[i+1]), float(all_numbers[i+2])]
                        total = sum(nums)
                        if 0.8 <= total <= 1.2:  # Allow some tolerance
                            normalized = [x/total for x in nums]
                            logger.debug(f"Parsed probabilities (fallback): {normalized}")
                            return normalized
                    except ValueError:
                        continue
            
            logger.warning(f"Could not parse probabilities from response: {response[:200]}...")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing probabilities: {e}")
            return None

def get_llm_client(model_name: Optional[str] = None) -> OllamaClient:
    """
    Get LLM client instance.
    
    Args:
        model_name (str, optional): Model name override
        
    Returns:
        OllamaClient: Configured client
    """
    if model_name is None:
        from core.config import config
        model_name = config.LLM_MODEL_NAME
    
    return OllamaClient(model_name=model_name) 