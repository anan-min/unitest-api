import ollama
import os
import re
import json
from typing import Dict, List, Optional
from prompts import GENERATE_UNIT_TEST_PROMPT, dotnet_example_code, ts_example_code
import asyncio


class UnitTestGenerator:
    def __init__(self, model_name: str = "qwen2.5:3b", host: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the Unit Test Generator

        Args:
            model_name (str): Name of the Ollama model to use
            host (str | None): Ollama server URL. Defaults to env OLLAMA_HOST/OLLAMA_BASE_URL or http://localhost:11434
            headers (dict | None): Optional headers to send with requests (e.g., auth)
        """
        self.model_name = model_name
        # Resolve host precedence: explicit > env (OLLAMA_HOST/OLLAMA_BASE_URL) > default localhost
        resolved_host = host or os.getenv("OLLAMA_HOST") or os.getenv(
            "OLLAMA_BASE_URL") or "http://localhost:11434" or "https://host.docker.internal:11434"
        self.client = ollama.Client(host=resolved_host, headers=headers or {})

    async def generate_unit_tests(self,
                                  code: str,
                                  model_name: Optional[str] = "qwen2.5:3b") -> Dict[str, str]:
        """
        Complete pipeline to generate unit tests from code

        Args:
            code (str): Source code to generate tests for
            language (str): Programming language
            test_framework (str): Testing framework to use
            model_name (str | None): Optional override for the model name per-call

        Returns:
            Dict[str, str]: Generated unit tests with metadata
        """
        # Generate the prompt
        prompt = self.generate_prompt(code)

        # Call Ollama
        response = await self.call_ollama(prompt, model_name=model_name)

        # Parse and return results
        parsed_result = self.parse_response(response)

        return {"test_code": parsed_result}

    async def get_available_models(self) -> List[str]:
        """
        Get list of available Ollama models

        Returns:
            List[str]: List of available model names
        """
        loop = asyncio.get_event_loop()

        def sync_call():
            try:
                models_response = self.client.list()
                if hasattr(models_response, 'models') and isinstance(models_response.models, list):
                    names = []
                    for model_obj in models_response.models:
                        # Try to get .model attribute (model name)
                        model_name = getattr(model_obj, 'model', None)
                        if model_name:
                            names.append(model_name)
                        else:
                            print(f"Model entry missing 'model': {model_obj}")
                    return names
                print(
                    "Ollama client.list() response does not have a 'models' attribute or is not a list.")
                return []
            except Exception as e:
                print(f"Error getting models: {str(e)}")
                return []
        return await loop.run_in_executor(None, sync_call)

    def generate_prompt(self, code: str) -> str:
        return GENERATE_UNIT_TEST_PROMPT.format(
            code=code,
        )

    async def call_ollama(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Send prompt to Ollama and get response

        Args:
            prompt (str): The formatted prompt
            model_name (str | None): Optional override for the model to use

        Returns:
            str: Raw response from Ollama
        """
        loop = asyncio.get_event_loop()

        def sync_call():
            try:
                response = self.client.chat(
                    model=model_name or self.model_name,
                    messages=[
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                )
                return response['message']['content']
            except Exception as e:
                raise Exception(f"Error calling Ollama: {str(e)}")
        return await loop.run_in_executor(None, sync_call)

    def parse_response(self, response: str) -> str:
        """
        Parse the LLM response to extract only the code content.
        Handles both code blocks (```...```) and raw code responses.

        Args:
            response (str): Raw response from Ollama

        Returns:
            str: Extracted code content

        Raises:
            ValueError: If response is empty
        """
        if not response or not response.strip():
            raise ValueError("Empty response from LLM")

        # First, try to find code blocks (```...```)
        code_block_pattern = r"```(?:[a-zA-Z0-9_+-]*\n?)?(.*?)```"
        code_matches = re.findall(code_block_pattern, response, re.DOTALL)

        if code_matches:
            # Return the largest code block if multiple exist
            largest_code = max(code_matches, key=len).strip()
            return largest_code

        # If no code blocks found, assume the entire response is code
        # (since our prompt asks for "only the test code")
        cleaned_response = response.strip()

        # Remove common non-code prefixes if they exist
        cleaned_response = re.sub(
            r'^(Here\'s|Here is|The code is|Code:|Solution:)[\s\S]*?:\s*', '', cleaned_response, flags=re.IGNORECASE)

        return cleaned_response


if __name__ == "__main__":
    unitTestGenerator = UnitTestGenerator()
    models = asyncio.run(unitTestGenerator.get_available_models())
    print(f"Available models: {models}")
    code = "def add(a, b):\n    return a + b"
    response = asyncio.run(unitTestGenerator.generate_unit_tests(code, model_name="qwen2.5:3b"))

    response2 = asyncio.run(unitTestGenerator.generate_unit_tests(ts_example_code, model_name="qwen2.5:3b"))
    print(f"Response 2: {response2}")

    reponse3 = asyncio.run(unitTestGenerator.generate_unit_tests(dotnet_example_code, model_name="qwen2.5:3b"))
    print(f"Response 3: {reponse3}")