import subprocess

TEMPLATE_NAMES = [
    'storytelling',
    'example_perturbation',
    'distracting_constraints',
    'negation_objective',
    'gameified',
    'domain_shift',
]

# Template for the sbatch script
script_template = """#!/bin/bash
#SBATCH -c 1
#SBATCH --mem=80G
#SBATCH -p gpu-preempt
#SBATCH --gpus-per-node=l40s:1
#SBATCH -t 24:00:00
#SBATCH -o sbatch_out/{template_name}.out

# Create log directory if not exists
mkdir -p log

# Run the command
python modify_problem.py --modify_type {template_name} --save_path {save_path} | tee log/{template_name}.log
"""

# Submit jobs for each template
for template_name in TEMPLATE_NAMES:
    print(f"Submitting job for TEMPLATE: {template_name}")
    save_path = f"data_modified/modified_problems_{template_name}.pkl"
    script_content = script_template.format(template_name=template_name, save_path=save_path)
    subprocess.run(["sbatch"], input=script_content.encode(), check=True)
