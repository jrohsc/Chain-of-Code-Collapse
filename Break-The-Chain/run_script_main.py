import subprocess

# Template for the sbatch script
script_template = """#!/bin/bash
#SBATCH -c 1                          # Number of Cores per Task
#SBATCH --mem=80G                 # Requested Memory in MB
#SBATCH -p gpu-preempt               # Partition
#SBATCH --gpus-per-node=a100:1      # A100 GPU
#SBATCH -t 24:00:00                  # Requested time
#SBATCH -o sbatch_out/{model_name}.out  # Stdout to this file

# Set the model name
MODEL={model_name}

# Create log directory if not exists
mkdir -p log

# Run the command
python main.py --model_name $MODEL | tee log/$MODEL.log
"""

# Loop over all models, datasets, modifications, and languages
model_name = 'qwq_32b'
print(f"Submitting job for MODEL: {model_name}")
# Format the script with current parameters
script_content = script_template.format(model_name=model_name)
# Submit the job via sbatch using standard input
subprocess.run(["sbatch"], input=script_content.encode(), check=True)