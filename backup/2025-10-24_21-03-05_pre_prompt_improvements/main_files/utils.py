import json
import os
import time
from datetime import datetime
from timeout_decorator import timeout, TimeoutError
from config.settings import DEBUG

def log_debug(message):
    """Log debug messages to app.txt if DEBUG is True."""
    if DEBUG:
        with open("app.txt", "a") as f:
            f.write(f"{datetime.now()}: {message}\n")

def save_json(data, filepath):
    """Save data to a JSON file, creating directories if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        log_debug(f"JSON saved to {filepath}")
    except Exception as e:
        log_debug(f"Error saving JSON to {filepath}: {e}")
        raise

def flatten_json(data):
    """Recursively flatten nested JSON structures."""
    flat = {}
    def flatten(d, parent_key=''):
        if isinstance(d, dict):
            for k, v in d.items():
                new_key = f"{parent_key}_{k}" if parent_key else k
                if isinstance(v, (dict, list)):
                    flatten(v, new_key)
                else:
                    flat[new_key] = v
        elif isinstance(d, list):
            for i, v in enumerate(d):
                new_key = f"{parent_key}_{i}"
                if isinstance(v, (dict, list)):
                    flatten(v, new_key)
                else:
                    flat[new_key] = v
    flatten(data)
    return flat

def parse_llm_json(llm, prompt, output_dir, filename, expected_keys=None, retries=3, flatten=True):
    """Parse LLM JSON output with optional flattening and error handling."""
    @timeout(120, timeout_exception=TimeoutError)
    def llm_with_timeout(llm, prompt):
        log_debug("Starting LLM call with timeout")
        response = llm.call(prompt)
        log_debug("LLM call completed")
        return response
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    for attempt in range(retries):
        try:
            log_debug(f"Attempt {attempt + 1} for {filename}")
            raw_response = llm_with_timeout(llm, prompt)
            log_debug(f"Raw LLM response for {filename}: '{raw_response}'")
            with open(filepath, "w") as f:
                f.write(raw_response)
            
            stripped_response = raw_response.strip()
            if not stripped_response:
                log_debug(f"LLM returned empty response for {filename}")
                continue
            
            # Strip markdown
            if stripped_response.startswith("```json") and stripped_response.endswith("```"):
                stripped_response = stripped_response[7:-3].strip()
            elif stripped_response.startswith("```") and stripped_response.endswith("```"):
                stripped_response = stripped_response[3:-3].strip()
            
            result = json.loads(stripped_response)
            processed_result = flatten_json(result) if flatten else result
            
            if expected_keys and flatten:
                if not all(k in processed_result for k in expected_keys):
                    raise ValueError(f"Flattened JSON missing expected keys: {expected_keys}")
            log_debug(f"Parsed JSON result for {filename}: {processed_result}")
            return processed_result
        except (json.JSONDecodeError, TimeoutError, ValueError) as e:
            log_debug(f"Error on attempt {attempt + 1} for {filename}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(1)
                continue
            log_debug(f"Failed after {retries} attempts, falling back to file: {filepath}")
            try:
                with open(filepath, "r") as f:
                    file_content = f.read().strip()
                log_debug(f"File content for fallback: '{file_content}'")
                
                if file_content.startswith("```json") and file_content.endswith("```"):
                    file_content = file_content[7:-3].strip()
                elif file_content.startswith("```") and file_content.endswith("```"):
                    file_content = file_content[3:-3].strip()
                
                result = json.loads(file_content)
                processed_result = flatten_json(result) if flatten else result
                
                if expected_keys and flatten:
                    if not all(k in processed_result for k in expected_keys):
                        raise ValueError(f"Fallback flattened JSON missing expected keys: {expected_keys}")
                return processed_result
            except (json.JSONDecodeError, FileNotFoundError, ValueError) as fe:
                log_debug(f"Failed to parse JSON fallback for {filename}: {str(fe)}")
                raise ValueError(f"Failed to parse JSON for {filename} after {retries} attempts and fallback: {str(fe)}")