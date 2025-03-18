from attack import *

function_map = {
    "naive": naive,
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