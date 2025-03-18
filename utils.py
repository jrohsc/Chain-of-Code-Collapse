import random
import re

## DeepSeek separate CoT and solution
def separate_thinking_and_solution(text):
    """
    Separates the generated text into two parts:
    1. The chain-of-thought (i.e. internal reasoning)
    2. The final solution code
    
    It first checks for a marker (</think>). If found, it splits the text at that point.
    Otherwise, it assumes that everything before the first code block is the reasoning.
    Then it extracts the first code block (delimited by triple backticks) as the solution.
    
    Returns:
        chain_thought (str): The internal reasoning part.
        solution_code (str): The final solution code.
    """
    # First, try to split using the </think> marker.
    if "</think>" in text:
        chain_thought, remainder = text.split("</think>", 1)
    else:
        # If no explicit marker is found, assume the chain-of-thought is before the first code block.
        parts = re.split(r"```", text, maxsplit=1)
        if len(parts) > 1:
            chain_thought = parts[0]
            remainder = "```" + parts[1]
        else:
            chain_thought = text
            remainder = ""
    
    # Extract the first code block as the solution code.
    code_blocks = re.findall(r"```(.*?)```", remainder, re.DOTALL)
    solution_code = code_blocks[0].strip() if code_blocks else ""
    
    return chain_thought.strip(), solution_code
