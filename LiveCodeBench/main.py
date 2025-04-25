import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from maps import model_map
import pandas as pd
from lcb_runner import evaluation
import json
from lcb_runner.evaluation.testing_util import run_test
from argparse import ArgumentParser
from tqdm import tqdm
import os
import torch

torch.cuda.empty_cache()

# Formatting Starter Code
FORMATTING_MESSAGE_WITH_STARTER_CODE = "You will use the following starter code to write the solution to the problem and enclose your code within delimiters."
FORMATTING_WITHOUT_STARTER_CODE = "Read the inputs from stdin solve the problem and write the answer to stdout (do not directly test on the row inputs). Enclose your code within delimiters as follows. Ensure that when the python program runs, it reads the inputs, runs the algorithm and writes output to STDOUT."

# Generic System Prompt
SYSTEM_MESSAGE_GENERIC = f"You are an expert Python programmer. You will be given a question (problem specification) and will generate a correct Python program that matches the specification and passes all tests."

class CodeGenerationProblem:
    def __init__(self, question_content, starter_code=None, difficulty=None, public_test_cases=None, private_test_cases=None):
        self.question_content = question_content
        self.starter_code = starter_code
        self.difficulty = difficulty
        self.public_test_cases = public_test_cases
        self.private_test_cases = private_test_cases

def dummy_guard(*args, **kwargs):
    # print("⚠️ reliability_guard skipped for notebook safety.")
    pass

def evaluate_code_with_row(row, generated_code: str, timeout: int = 30, debug: bool = False):
    """
    Evaluate a solution against public test cases from a LiveCodeBench row.
    Automatically uses call-based or standard_input mode depending on metadata.

    Args:
        row: A row from your benchmark DataFrame.
        generated_code: Python solution (either class-based or standard I/O).
        timeout: Max seconds allowed for execution.
        debug: Print debug info.

    Returns:
        result: Evaluation scores per test.
        metadata: Execution trace including inputs, outputs, errors, etc.
    """
    if not row.get("public_test_cases"):
        print("⚠️ No public test cases found in this row.")
        return None, None

    # Load test cases
    public_tests = json.loads(row["public_test_cases"])
    input_lines = [tc["input"].strip() for tc in public_tests]
    output_lines = [tc["output"].strip() for tc in public_tests]

    fn_name = None
    try:
        metadata = json.loads(row.get("metadata", "{}"))
        fn_name = metadata.get("func_name")
    except Exception as e:
        print(f"⚠️ Failed to parse metadata: {e}")

    row = {
        "input_output": json.dumps({
            "inputs": input_lines,
            "outputs": output_lines,
            **({"fn_name": fn_name} if fn_name else {})
        }),
        "code": ""
    }

    return run_test(row, test=generated_code, timeout=timeout, debug=debug)

def extract_solution_code(output):
    # Try extracting from ```python ... ``` first
    match = re.search(r"```python\s*(.*?)```", output, re.DOTALL)

    # Fallback to plain ``` ... ``` if no language specified
    if not match:
        match = re.search(r"```\s*(.*?)```", output, re.DOTALL)

    # Extract and clean
    solution_code = match.group(1).strip() if match else None
    return solution_code
    
def get_generic_question_template_answer(question: CodeGenerationProblem):
    prompt = f"### Question:\n{question.question_content}\n\n"
    if question.starter_code:
        prompt += (
            f"### Format: {FORMATTING_MESSAGE_WITH_STARTER_CODE}\n"
        )
        prompt += f"```python\n{question.starter_code}\n```\n\n"
    else:
        prompt += f"### Format: {FORMATTING_WITHOUT_STARTER_CODE}\n"
        prompt += "```python\n# YOUR CODE HERE\n```\n\n"
    prompt += f"### Answer: (use the provided format with backticks)\n\n"
    return prompt

# Function to log each result
def log_result_to_csv(csv_path, question_content, difficulty, model, public_test_cases,
                      output, solution_code, result, metadata_output):
    row = {
        "question_content": question_content,
        "difficulty": difficulty,
        "model": model,
        "public_test_cases": public_test_cases,
        "output": output,
        "solution_code": solution_code,
        "result": result,
        "metadata_output": metadata_output
    }

    # Convert to DataFrame with a single row and append to CSV
    df = pd.DataFrame([row])
    df.to_csv(csv_path, mode='a', header=False, index=False)

def main():
    parser = ArgumentParser()
    parser.add_argument('--model_name', type=str, default='qwen_coder')
    args = parser.parse_args()
    model_name = args.model_name

    # Load tokenizer
    model_directory = model_map[model_name]
    tokenizer = AutoTokenizer.from_pretrained(model_directory)
    # Load model with float16 precision
    model = AutoModelForCausalLM.from_pretrained(
        model_directory,
        torch_dtype=torch.float16,
        device_map="auto"  # or device_map={"": 0} if only 1 GPU
    )

    # Create pipeline using loaded model + tokenizer
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=100000,
    )

    pkl_path = 'data/code_generation_lite.pkl'
    df = pd.read_pickle(pkl_path)
    df = df[df['platform'] == 'leetcode'].reset_index()

    # Define CSV path
    csv_path = f"results/clean/evaluation_log_{model_name}.csv"
    columns = [
        "question_content", "difficulty", "model", "public_test_cases",
        "output", "solution_code", "result", "metadata_output"
    ]

    # Load already-evaluated question contents
    if os.path.exists(csv_path):
        completed_df = pd.read_csv(csv_path)
        completed_questions = set(completed_df["question_content"])
        print(f"✅ Resuming from row {len(completed_questions)} / {len(df)}")
    else:
        pd.DataFrame(columns=columns).to_csv(csv_path, index=False)
        completed_questions = set()

    evaluation.testing_util.reliability_guard = dummy_guard

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        if row["question_content"] in completed_questions:
            print("Skip...")
            continue  # ✅ Skip already evaluated rows

        problem = CodeGenerationProblem(
            question_content=row["question_content"],
            starter_code=row["starter_code"] if row["starter_code"] else None,
            difficulty=row['difficulty'],
            public_test_cases=row['public_test_cases'],
            private_test_cases=row['private_test_cases'],
        )
        
        prompt = get_generic_question_template_answer(problem)
        
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE_GENERIC},
            {"role": "user", "content": prompt},
        ]

        response = pipe(messages)
        output = response[0]['generated_text'][2]['content']
        generated_code = extract_solution_code(output)

        if generated_code is None:
            result, metadata_output = None, {"error_message": "No code extracted", "error_code": -1}
            log_result_to_csv(
                csv_path, row["question_content"], row["difficulty"], model_name,
                row["public_test_cases"], output, generated_code, result, metadata_output
            )
            continue

        try:
            result, metadata_output = evaluate_code_with_row(row, generated_code, timeout=30, debug=True)
        except Exception as e:
            print(f"⚠️ Skipping row due to evaluation error: {e}")
            result, metadata_output = None, {
                "error_message": f"Exception: {str(e)}",
                "error_code": -999
            }

        log_result_to_csv(
            csv_path, row["question_content"], row["difficulty"], model_name,
            row["public_test_cases"], output, generated_code, result, metadata_output
        )

if __name__ == '__main__':
    main()