import time
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
import anthropic
import google.generativeai as genai
from google.generativeai import GenerativeModel

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
def log_result_to_csv(perturbation_type, csv_path, orig_question_content, modified_question_content, difficulty, model, public_test_cases,
                      output, solution_code, result, metadata_output):
    row = {
        "perturbation_type": perturbation_type,
        "orig_question_content": orig_question_content,
        "modified_question_content": modified_question_content,
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
    parser.add_argument('--perturbation_type', type=str, default='storytelling')
    args = parser.parse_args()

    perturbation_type = args.perturbation_type
    model_name = args.model_name
    model_name_split = model_name.split('-')

    print(f'model_name: {model_name}')

    if 'claude' in model_name_split:
        print("Running Claude API...")
        ANTHROPIC_API_KEY='ENTER_KEY'
        model = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    elif 'gemini' in model_name_split:
        print("Running Gemini API...")
        genai.configure(api_key='ENTER_KEY')
        model = GenerativeModel(model_name)
        
    else:
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
        model = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=8192,
        )

    pkl_path = f'data_modified/modified_problems_{perturbation_type}.pkl'
    df = pd.read_pickle(pkl_path).iloc[:100]

    # Define CSV path
    csv_path = f"results/attacked/evaluation_log_{model_name}_{perturbation_type}.csv"
    print(f"csv_path: {csv_path}")
    columns = [
        "perturbation_type", "orig_question_content", "modified_question_content", "difficulty", "model", "public_test_cases",
        "output", "solution_code", "result", "metadata_output"
    ]

    # Load already-evaluated question contents
    if os.path.exists(csv_path):
        completed_df = pd.read_csv(csv_path)
        completed_questions = set(completed_df["modified_question_content"])
        print(f"✅ Resuming from row {len(completed_questions)} / {len(df)}")
    else:
        pd.DataFrame(columns=columns).to_csv(csv_path, index=False)
        completed_questions = set()

    evaluation.testing_util.reliability_guard = dummy_guard

    for idx, row in tqdm(df.iterrows(), total=100):
        if row[f"{perturbation_type}_modified"] in completed_questions:
            print("Skip...")
            continue  # ✅ Skip already evaluated rows

        problem = CodeGenerationProblem(
            question_content=row[f"{perturbation_type}_modified"],
            starter_code=row["starter_code"] if row["starter_code"] else None,
            difficulty=row['difficulty'],
            public_test_cases=row['public_test_cases'],
            private_test_cases=row['private_test_cases'],
        )
        
        prompt = get_generic_question_template_answer(problem)

        ### Generation ###
        try:
            if 'claude' in model_name_split:
                message = model.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=1,
                system=SYSTEM_MESSAGE_GENERIC,
                messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                )
                output = message.content[0].text

            elif 'gemini' in model_name_split:
                time.sleep(56)
                response = model.generate_content(f"{SYSTEM_MESSAGE_GENERIC}\n\n{prompt}")
                try:
                    output = response.candidates[0].content.parts[0].text
                except Exception as e:
                    print(f"⚠️ Failed to parse Gemini output: {e}")
                    result, metadata_output = None, {
                        "error_message": f"Gemini output parsing error: {str(e)}",
                        "error_code": -3
                    }
                    log_result_to_csv(
                        perturbation_type, csv_path, row["question_content"], row[f"{perturbation_type}_modified"],
                        row["difficulty"], model_name, row["public_test_cases"],
                        None, None, result, metadata_output
                    )
                    continue

            else:
                messages = [
                    {"role": "system", "content": SYSTEM_MESSAGE_GENERIC},
                    {"role": "user", "content": prompt},
                ]
                response = model(messages)
                output = response[0]['generated_text'][2]['content']
            
            generated_code = extract_solution_code(output)

        except (ValueError, IndexError, KeyError) as e:
            print(f"⚠️ Skipping due to response error or output too long: {e}")
            result, metadata_output = None, {
                "error_message": f"Generation error: {str(e)}",
                "error_code": -2
            }
            log_result_to_csv(
                perturbation_type, csv_path, row["question_content"], row[f"{perturbation_type}_modified"],
                row["difficulty"], model_name, row["public_test_cases"],
                None, None, result, metadata_output
            )
            continue

        if generated_code is None:
            result, metadata_output = None, {"error_message": "No code extracted", "error_code": -1}
            log_result_to_csv(
                perturbation_type, csv_path, row["question_content"], row[f"{perturbation_type}_modified"],
                row["difficulty"], model_name, row["public_test_cases"],
                output, generated_code, result, metadata_output
            )
            continue


        if generated_code is None:
            result, metadata_output = None, {"error_message": "No code extracted", "error_code": -1}
            log_result_to_csv(
                perturbation_type, csv_path, row["question_content"], row[f"{perturbation_type}_modified"], row["difficulty"], model_name,
                row["public_test_cases"], output, generated_code, result, metadata_output
            )
            continue

        try:
            result, metadata_output = evaluate_code_with_row(row, generated_code, timeout=30, debug=True)
            # result, metadata_output = safe_run_test(row, generated_code, timeout=30)
        except Exception as e:
            print(f"⚠️ Skipping row due to evaluation error: {e}")
            result, metadata_output = None, {
                "error_message": f"Exception: {str(e)}",
                "error_code": -999
            }

        log_result_to_csv(
            perturbation_type, csv_path, row["question_content"], row[f"{perturbation_type}_modified"],
            row["difficulty"], model_name, row["public_test_cases"],
            output, generated_code, result, metadata_output
        )

if __name__ == '__main__':
    main()
