JUDGE = """
You are an expert code evaluator with deep experience in reviewing and validating code solutions. Your task is to assess the quality of a generated code solution for a given problem.

Below are the details:

[Problem Description]:
{problem_description}

[Generated Code]:
```python
{generated_code}

[Expected Solution]:
{expected_solution}

Please evaluate the generated code using the following criteria:
1. Correctness: Does the generated code implement the intended solution accurately? Consider whether the code produces the expected output for all relevant test cases.
2. Completeness: Does the code address all parts of the problem and cover any edge cases mentioned in the problem description?
3. Clarity: Is the code well-structured, easy to read, and appropriately commented or named so that its logic is clear?

In the generation, only output either "correct" or "incorrect". No additional comments should be contained in the output.
"""

########################################################################################################################################################################################################################
REASONING_JUDGE = """
You are an expert code evaluator with extensive experience in reviewing and validating code solutions. Your tasks:

1. **Correctness**  
   Determine if the generated code correctly implements the problem requirements and produces the correct outputs for relevant test cases.

2. **Completeness**  
   Verify whether the code addresses all parts of the problem statement, including any edge cases.

3. **Reasoning Capability (Score: 1–5)**  
   Assign a single integer score (1 through 5) that reflects the *quality* of the model’s reasoning process, based on:
   - **Logical Consistency**: Are the steps and explanations in the reasoning tokens coherent and consistent with the final code solution?
   - **Depth of Analysis**: Does the reasoning consider edge cases, potential pitfalls, or complexities in the problem?
   - **Clarity and Thoroughness**: How clear and step-by-step is the thought process leading to the final code?

   Use the following guidelines when assigning a reasoning score:
   - **1** – Severely flawed or nearly no reasoning; the steps are largely nonsensical or not connected to the final solution.
   - **2** – Minimal or weak reasoning; partially incomplete, confusing, or mostly guesswork.
   - **3** – Adequate reasoning; some steps are missing or not fully explained, but the general thought process is acceptable.
   - **4** – Good reasoning; mostly sound, covers core steps, and mentions some (but not all) edge cases.
   - **5** – Excellent reasoning; thorough explanation, covers all steps logically, and addresses relevant edge cases comprehensively.

4. **Final Output**
   - In your final answer, output **only** two pieces of information:
     1. The reasoning score (1–5).
     2. The correctness verdict, which is either `"correct"` or `"incorrect"`.
   - No additional commentary, explanation, or text should appear beyond these two pieces of information.

---

### [Problem Description]
{problem_description}

### [Reasoning Tokens]
{reasoning_tokens}

### [Generated Code] (python)
{generated_code}

**Your Output Format (and nothing else):**  
**Correctness:**
**Reasoning Score:**
"""
########################################################################################################################################################################################################################

EVAL_EXISTING = """
You are an imperial judge to determine whether the given text suggests that the evaluation represents "correct" or "incorrect".

Below are the details:

[Evaluation Result]:
{eval_result}

In the generation, only output either "correct" or "incorrect". No additional comments should be contained in the output.
"""
