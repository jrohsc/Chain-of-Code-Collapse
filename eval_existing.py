import os
import glob
import pandas as pd
from prompt_template import EVAL_EXISTING
from maps import model_map
from tqdm import tqdm
from transformers import pipeline
from argparse import ArgumentParser
import torch

def main():
    parser = ArgumentParser()
    parser.add_argument('--target_model', type=str, default='deepseek_7b')
    parser.add_argument('--judge_model', type=str, default='llama_3_1_8B_it')
    parser.add_argument('--attack_method', type=str, required=True, default="irrelevant")
    args = parser.parse_args()

    # csv_files = glob.glob(os.path.join('csv', '*.csv'))

    model_dir = model_map['llama_3_1_8B_it']
    pipe = pipeline("text-generation", 
                            model=model_dir,
                            torch_dtype=torch.float16,
                            max_length=8024,
                            device=0)

    csv_path = f"target_{args.target_model}_judge_{args.judge_model}_attack_{args.attack_method}.csv"
    csv_path = os.path.join('csv', csv_path)
    print(f"csv_path: {csv_path}")

    df = pd.read_csv(csv_path, index_col=0)
    df['final_eval_result'] = None

    for idx, row in tqdm(df.iterrows()):
        if row['final_eval_result'] != None:
            print("Already processed...")
            continue
        eval_result = row['eval_result']
        prompt = EVAL_EXISTING.format(eval_result=eval_result)

        messages = [
            {"role": "user", "content": prompt},
        ]
        final_eval_result = pipe(messages)
        final_eval_result = final_eval_result[0]['generated_text'][1]['content']

        print(f"final_eval_result: {final_eval_result}")

        df.at[idx, 'final_eval_result'] = final_eval_result
        df.to_csv(csv_path)
    
    ASR = list(df['final_eval_result'].count('incorrect')) / len(df)

    print("*"*50)
    print(f"path: {csv_path}")
    print(f"ASR: {ASR}")
    print("*"*50)

if __name__ == '__main__':
    main()