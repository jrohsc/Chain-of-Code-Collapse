from attack import *
import subprocess

attacks = ['alter', 'irrelevant', 'paraphrase', 'naive']
# target_models = ['deepseek_7b', 'deepseek_14b', 'deepseek_32b', 'qwen_2_5_7b', 'qwq_32b', 'llama_3_1_8B_it']
target_models = ['deepseek_7b', 'qwen_2_5_7b']

# Template for the sbatch script
script_template = """#!/bin/bash
#SBATCH -c 1            # Number of Cores per Task
#SBATCH --mem=100000     # Requested Memory in MB
#SBATCH -p gpu-preempt  # Partition
#SBATCH --gpus-per-node=a100:1 # A100
#SBATCH -t 24:00:00     # Requested time
#SBATCH -o sbatch_out/{target_model}_{judge_model}_{attack_method}.out   # Output file based on model, dataset, lang, and modification

# Set parameters
TARGET={target_model}
JUDGE={judge_model}
ATTACK={attack_method}

# Automatically generate output file names based on parameters
LOG="log/${{TARGET}}_${{JUDGE}}_${{ATTACK}}.log"

# Run the command
python main.py --target_model $TARGET --judge_model $JUDGE --attack_method $ATTACK --end_index 300 | tee $LOG
"""

# Loop over all models, datasets, modifications, and languages
judge_model = "llama_3_1_8B_it"

for target_model in target_models:
    for attack in attacks:
        print(f"Submitting job for TARGET: {target_model}, JUDGE: {judge_model}, ATTACK: {attack}")
        # Format the script with current parameters
        script_content = script_template.format(target_model=target_model, judge_model=judge_model, attack_method=attack)
        # Submit the job via sbatch using standard input
        subprocess.run(["sbatch"], input=script_content.encode(), check=True)