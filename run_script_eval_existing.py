from attack import *
import subprocess

function_map = {
    "alter": alter_numbers,
    "irrelevant": add_irrelevant_clause,
    "paraphrase": paraphrase_text
}

model_map = {
    'deepseek_7b': "/datasets/ai/deepseek/hub/models--deepseek-ai--DeepSeek-R1-Distill-Qwen-7B/snapshots/6602cadec947dbb53e64f3d8d6425320b2197247",
    'deepseek_14b': "/datasets/ai/deepseek/hub/models--deepseek-ai--DeepSeek-R1-Distill-Qwen-14B/snapshots/5ee96d8a09692e87087a6e0496d87124a1cdc3fe",
    'deepseek_32b': "/datasets/ai/deepseek/hub/models--deepseek-ai--DeepSeek-R1-Distill-Qwen-32B/snapshots/3865e12a1eb7cbd641ab3f9dfc28c588c6b0c1e9",
    'qwen_2_5_7b': "/datasets/ai/qwen/hub/models--Qwen--Qwen2.5-Math-7B-Instruct/snapshots/ef9926d75ab1d54532f6a30dd5e760355eb9aa4d",
    'qwq_32b': "/datasets/ai/qwen/hub/models--Qwen--QwQ-32B-Preview/snapshots/91906fe41a48b6a89ce2970abfd1269eefee170e",
    'llama_3_1_8B_it': "/datasets/ai/llama3/hub/models--meta-llama--Meta-Llama-3.1-8B-Instruct/snapshots/5206a32e0bd3067aef1ce90f5528ade7d866253f"
}

# Template for the sbatch script
script_template = """#!/bin/bash
#SBATCH -c 1            # Number of Cores per Task
#SBATCH --mem=100000     # Requested Memory in MB
#SBATCH -p gpu-preempt  # Partition
#SBATCH --gpus-per-node=a100:1 # A100
#SBATCH -t 24:00:00     # Requested time
#SBATCH -o sbatch_out/eval_existing_{target_model}_{judge_model}_{attack_method}.out   # Output file based on model, dataset, lang, and modification

# Set parameters
TARGET={target_model}
JUDGE={judge_model}
ATTACK={attack_method}

# Automatically generate output file names based on parameters
LOG="log/${{TARGET}}_${{JUDGE}}_${{ATTACK}}.log"

# Run the command
python eval_existing.py --target_model $TARGET --judge_model $JUDGE --attack_method $ATTACK | tee $LOG
"""

# Loop over all models, datasets, modifications, and languages
judge_model = "llama_3_1_8B_it"
target_models = list(model_map.keys())
attacks = list(function_map.keys())

for target_model in target_models:
    for attack in attacks:
        print(f"Submitting job for TARGET: {target_model}, JUDGE: {judge_model}, ATTACK: {attack}")
        # Format the script with current parameters
        script_content = script_template.format(target_model=target_model, judge_model=judge_model, attack_method=attack)
        # Submit the job via sbatch using standard input
        subprocess.run(["sbatch"], input=script_content.encode(), check=True)