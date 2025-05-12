import subprocess

TEMPLATE_NAMES = [
    'storytelling',
    'example_perturbation',
    'distracting_constraints',
    'negation_objective',
    'gameified',
    'domain_shift',
]

target_models = ['deepseek_7b', 'deepseek_14b', 'deepseek_32b', 'qwen_coder', 'qwq_32b', 'llama_3_1_8B_it']

# Template for the sbatch script
script_template = """#!/bin/bash
#SBATCH -c 1                          # Number of Cores per Task
#SBATCH --mem=80G                 # Requested Memory in MB
#SBATCH -p gpu-preempt               # Partition
#SBATCH --gpus-per-node=l40s:1      # A100 GPU
#SBATCH -t 24:00:00                  # Requested time
#SBATCH -o sbatch_out/{perturbation_type}_{model_name}-%j.out  # Stdout to this file

# Set the model name
MODEL={model_name}
PERTURBATION_TYPE={perturbation_type}

# Create log directory if not exists
mkdir -p log

# Run the command
python main_perturbation.py --model_name $MODEL --perturbation_type $PERTURBATION_TYPE | tee log/$MODEL.log
"""

for model_name in target_models:
    for perturbation_type in TEMPLATE_NAMES:
        # Loop over all models, datasets, modifications, and languages
        print(f"Submitting job for MODEL: {model_name} | PERTURBATION: {perturbation_type}")
        # Format the script with current parameters
        script_content = script_template.format(model_name=model_name, perturbation_type=perturbation_type)
        # Submit the job via sbatch using standard input
        subprocess.run(["sbatch"], input=script_content.encode(), check=True)