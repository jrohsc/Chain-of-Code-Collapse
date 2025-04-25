import re
import os
import pandas as pd
from datasets import load_dataset
import torch
from transformers import pipeline
from argparse import ArgumentParser
from prompt_template import REASONING_JUDGE
from utils import separate_thinking_and_solution
from attack import *
from maps import *

def pattern_matching(output_text):
    """
    Extracts correctness and reasoning score from output_text using regex.
    Handles both markdown-style (bold `**text:**`) and plain text formats.
    """
    # Regex patterns to capture numbers and words after "Reasoning Score:" and "Correctness:"
    reasoning_pattern = r'(?:\*\*Reasoning Score:\*\*|Reasoning Score:)\s*(\d+)'
    correctness_pattern = r'(?:\*\*Correctness:\*\*|Correctness:)\s*(\w+)'

    # Search for Reasoning Score
    score_match = re.search(reasoning_pattern, output_text)
    reasoning_score = int(score_match.group(1)) if score_match else 0  # Return 0 instead of NaN

    # Search for Correctness
    correctness_match = re.search(correctness_pattern, output_text)
    correctness = correctness_match.group(1) if correctness_match else "unknown"  # Default to "unknown" if missing

    return correctness, reasoning_score

def main():
    parser = ArgumentParser()
    parser.add_argument('--target_model', type=str, default='deepseek_7b')
    parser.add_argument('--judge_model', type=str, default='llama_3_1_8B_it')
    parser.add_argument('--attack_method', type=str, required=True, default="irrelevant")
    parser.add_argument('--max_questions', type=int, default=None, help="Maximum number of new questions to process in this run")
    parser.add_argument('--end_index', type=int, default=200, help="Process only questions with index less than this value")
    args = parser.parse_args()

    # Attack method
    attack_func = function_map[args.attack_method]

    target_dir = model_map[args.target_model]
    target_model = pipeline("text-generation", 
                            model=target_dir,
                            torch_dtype=torch.float16,
                            max_length=8024,
                            device=0)

    # LLama-as-a-Judge
    judge_dir = model_map[args.judge_model]
    judge_model = pipeline("text-generation", 
                           model=judge_dir,
                           torch_dtype=torch.float16,
                           max_length=8024,
                           device=0)

    # Load Leetcode dataframe
    ds = load_dataset("greengerong/leetcode")['train']
    df = pd.DataFrame.from_dict(ds)

    # If an end index is specified, process only up to that question
    if args.end_index is not None:
        df = df.iloc[:args.end_index]

    csv_filename = f"target_{args.target_model}_judge_{args.judge_model}_attack_{args.attack_method}.csv"
    csv_path = os.path.join('csv_modified', csv_filename)
    columns = ['model', 'difficulty', 'orig_question', 'ground_truth', 'attacked_question', 'cot', 'response', 'eval_result', 'correctness', 'reasoning_score']

    # Check if CSV already exists to resume from previous run
    if os.path.exists(csv_path):
        results_df = pd.read_csv(csv_path)
        processed_questions = set(results_df['orig_question'])
        print(f"Resuming run: {len(processed_questions)} questions already processed.")
    else:
        results_df = pd.DataFrame(columns=columns)
        processed_questions = set()

    # Filter out already processed questions
    unprocessed_df = df[~df['content'].isin(processed_questions)]
    if args.max_questions is not None:
        unprocessed_df = unprocessed_df.iloc[:args.max_questions]

    for idx, row in unprocessed_df.iterrows():
        try:
            difficulty = row['difficulty']
            orig_question = row['content']
            ground_truth = row['python']

            attacked_question = attack_func(orig_question)
            messages = [
                {"role": "system", "content": "Solve in Python code"},
                {"role": "user", "content": attacked_question},
            ]

            result = target_model(messages)[0]['generated_text'][2]['content']
            cot, response = separate_thinking_and_solution(result)

            # Prepare Judge prompt
            judge_prompt = REASONING_JUDGE.format(problem_description=orig_question, 
                                                  reasoning_tokens=cot,
                                                  generated_code=response)

            judge_messages = [
                {"role": "user", "content": judge_prompt},
            ]
            eval_result = judge_model(judge_messages)
            eval_result = eval_result[0]['generated_text'][1]['content']
            correctness, reasoning_score = pattern_matching(eval_result)

            print(correctness)      # "correct"
            print(reasoning_score)  # "5"


            print("*" * 50)
            print(f"Index: {idx}")
            print(f"Model: {args.target_model}")
            print(f"Difficulty: {difficulty}")
            print(f"Original Question: {orig_question}")
            print(f"Attacked Question: {attacked_question}")
            print(f"CoT: {cot}")
            print(f"Response: {response}")
            print(f"Evaluation Result: {eval_result}")
            print(f"correctness: {correctness}")
            print(f"reasoning_score: {reasoning_score}")
            print("*" * 50)

            new_row = {
                'model': args.target_model,
                'difficulty': difficulty,
                'orig_question': orig_question,
                'ground_truth': ground_truth,
                'attacked_question': attacked_question,
                'cot': cot,
                'response': response,
                'eval_result': eval_result,
                'correctness': correctness,
                'reasoning_score': reasoning_score
            }

            new_idx = len(results_df)
            results_df.loc[new_idx] = new_row
            results_df.to_csv(csv_path, index=False)
        except Exception as e:
            print(f"Error processing index {idx}: {e}")
            continue

if __name__ == '__main__':
    main()
