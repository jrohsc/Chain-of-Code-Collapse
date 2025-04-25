from tqdm import tqdm
from maps import model_map
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import pandas as pd
from argparse import ArgumentParser
from PROMPT_TEMPLATE import PROMPT_TEMPLATES

def main():
    parser = ArgumentParser()
    parser.add_argument('--perturbation_type', type=str, default='storytelling')
    parser.add_argument('--save_path', type=str, default='modified_problems.pkl')
    args = parser.parse_args()

    perturbation_type = args.perturbation_type
    save_path = args.save_path

    # Load prompt template
    TEMPLATE = PROMPT_TEMPLATES[perturbation_type]

    # Use LLaMA-3.1-8B-Instruct
    model_name = 'llama_3_1_8B_it'
    model_directory = model_map[model_name]
    tokenizer = AutoTokenizer.from_pretrained(model_directory)

    model = AutoModelForCausalLM.from_pretrained(
        model_directory,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=4028,
        return_full_text=False
    )

    # Load dataset
    df = pd.read_pickle('data/code_generation_lite.pkl')
    df = df[df['platform'] == 'leetcode'].reset_index(drop=True)

    # Initialize empty column to store outputs
    df[f"{perturbation_type}_modified"] = ""

    for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"Modifying ({perturbation_type})"):
        original_content = row['question_content']
        prompt = TEMPLATE.format(original_content=original_content)

        messages = [{"role": "user", "content": prompt}]
        
        response = pipe(messages)
        print(response)
        output = response[0]['generated_text']

        # Save result to DataFrame and immediately persist to disk
        df.at[idx, f"{perturbation_type}_modified"] = output
        df.to_pickle(save_path)

    print(f"\nSaved modified DataFrame (final) to: {save_path}")

if __name__ == '__main__':
    main()
