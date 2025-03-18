import random
import re

def naive(text):
    return text

def alter_and_irrelevant(text: str) -> str:
    """Modify text by altering numbers slightly and appending an irrelevant clause."""
    
    def tweak_num(match):
        """Modify numeric values by adding or subtracting a small value."""
        num_str = match.group(0)
        try:
            num_val = int(num_str)
            return str(num_val + random.choice([-1, +1]))
        except:
            try:
                num_val = float(num_str)
                delta = 0.1 * num_val  # Modify float values by 10%
                return str(num_val + delta)
            except:
                return num_str  # Return as is if not purely numeric

    # Step 1: Alter numbers in the text
    modified_text = re.sub(r'\d+(\.\d+)?', tweak_num, text)
    
    # Step 2: Append an irrelevant clause
    distractors = [
        "Additionally, the sky was clear that day.", 
        "Note that this information might not be relevant to the problem at hand.", 
        "John also has a completely unrelated question in mind."
    ]
    modified_text += " " + random.choice(distractors)
    
    return modified_text

def alter_numbers(text: str) -> str:
    """Find numbers in the text and alter them slightly (e.g., +1 or -1)."""
    def tweak_num(match):
        num_str = match.group(0)
        # If the number is an integer, add or subtract 1; if decimal, small perturbation
        try:
            num_val = int(num_str)
            return str(num_val + random.choice([-1, +1]))
        except:
            try:
                num_val = float(num_str)
                delta = 0.1 * num_val  # 10% change for floats
                return str(num_val + delta)
            except:
                return num_str  # if it's not purely numeric, return as is
    return re.sub(r'\d+(\.\d+)?', tweak_num, text)

def add_irrelevant_clause(text: str) -> str:
    """Append an irrelevant but plausible sentence to the text."""
    distractors = [
        "Additionally, the sky was clear that day.", 
        "Note that this information might not be relevant to the problem at hand.", 
        "John also has a completely unrelated question in mind."
    ]
    return text.strip() + " " + random.choice(distractors)

def paraphrase_text(text: str) -> str:
    """A simple (non-learning) paraphrasing by restructuring the sentence."""
    # This is a naive approach: split into clauses and shuffle or replace some words.
    # (For a real paraphrase, one might use a synonym dictionary or a T5 model, etc.)
    synonyms = {"find": "determine", "number": "quantity", "apple": "fruit"}
    # Replace some words with synonyms:
    words = text.split()
    words = [synonyms.get(w.lower(), w) for w in words]
    paraphrased = " ".join(words)
    # Simple structural change: add a redundant phrase at the beginning.
    paraphrased = "Considering the aforementioned details, " + paraphrased
    return paraphrased


