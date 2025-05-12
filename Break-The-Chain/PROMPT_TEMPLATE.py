PROMPT_TEMPLATES = {
    "storytelling": """
        You are a helpful assistant that rewrites programming problems into a storytelling format, while keeping the original intent and structure. 
        Keep the **Input**, **Output**, **Explanation**, **Example**, and **Constraints** sections intact, but frame the initial description like a story to engage the reader.

        Here is the original problem:

        {original_content}

        Now, rewrite it in a storytelling format, making the introduction engaging and fun, like a problem told by a narrator or part of a programming adventure story.
        No additional explanation needed. Just output the modified problem:
    """,

    "example_perturbation": """
        You are a helpful assistant that modifies coding problems keeping the **Input**, **Output**, **Explanation** and **Constraints** sections.

        However, your task is to **perturb the examples to make them more confusing for language models**. Do this by:
        - Shuffling values (e.g., make phone numbers look like ages, and vice versa),
        - Mixing genders randomly,
        - Using near-threshold ages (e.g., 59, 60, 61),
        - Placing the valid cases in less obvious positions (e.g., only the last passenger meets the criteria),
        - Inserting redundant or distracting patterns in phone/seat numbers.

        Your goal is to **preserve correctness** (the logic of the output must still match the modified input), but make the **examples harder for a model to pattern-match**.

        Here is the original problem:

        {original_content}

        Now, modify only the examples to make them as confusing and misleading as possible while keeping them valid and aligned with the logic.
        No additional explanation needed. Just output the modified problem:
    """,

    "distracting_constraints": """
        You are a helpful assistant that modifies coding problems while keeping the **Input**, **Output**, **Explanation**, and **Example** sections intact.

        Your task is to inject **redundant or distracting constraints** into the problem. Specifically:
        - Add conditions that are irrelevant to the solution (e.g., "elements are sorted", "input is a palindrome").
        - Mention edge cases that don’t matter.
        - Add domain-specific lingo or properties that may confuse models.

        These changes should increase cognitive load without changing the fundamental logic or solvability.

        Here is the original problem:

        {original_content}

        Now, modify it by inserting confusing but logically irrelevant constraints and background context.
        No additional explanation needed. Just output the modified problem:
    """,

    "negation_objective": """
        You are a helpful assistant that modifies coding problems, keeping the **Input**, **Output**, **Explanation**, and **Constraints** sections.

        Your task is to **invert the problem’s objective**. For example:
        - If the goal is to find the maximum, make it minimum.
        - If it asks for “increasing”, ask for “not increasing”.
        - If it asks to "include", switch to "exclude" or "avoid".

        Ensure the examples and output are updated accordingly while preserving the core structure and difficulty.

        Here is the original problem:

        {original_content}

        Now, rewrite it with the **opposite objective**, maintaining the same format.
        No additional explanation needed. Just output the modified problem:
    """,

    "gameified": """
        You are a helpful assistant that transforms coding problems into a **game-like or story-based format**.

        Your goals are:
        - Keep the **Input**, **Output**, **Explanation**, and **Constraints** intact.
        - Turn the task into a challenge involving players, agents, or scenarios.
        - Introduce a thematic layer (e.g., “Alice wants to win”, “a robot navigating cells”) while keeping the logic equivalent.

        Here is the original problem:

        {original_content}

        Now, rewrite it as a challenge-based or narrative problem while preserving semantics.
        No additional explanation needed. Just output the modified problem:
    """,

    "domain_shift": """
        You are a helpful assistant that rewrites coding problems in a different **domain or context**.

        Instructions:
        - Keep **Input**, **Output**, **Explanation**, and **Constraints** unchanged.
        - Replace terms with domain-specific equivalents (e.g., convert numbers to elevator floors, jobs, floors, days).
        - Maintain logic exactly, but alter terminology so the surface form is different.

        Here is the original problem:

        {original_content}

        Now, modify the domain and terminology (e.g., change "array of integers" to "daily revenue"), but keep the logic identical.
        No additional explanation needed. Just output the modified problem:
    """
}
