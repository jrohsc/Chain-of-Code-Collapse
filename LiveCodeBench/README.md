# BREAK-THE-CHAIN: Adversarial Prompting in Code Generation

📄 Paper (Coming Soon)  
📂 [Dataset on Google Drive]([https://drive.google.com/drive/u/2/folders/1QZX7q1Y7gf7wqRxrTIaBYcZO9CA4wX7c](https://drive.google.com/drive/folders/1E1Zoj1Ke1z_OpJePjEUMF2IPv5IqtE2F?usp=sharing))  

---

## 🧠 Overview

**BREAK-THE-CHAIN** introduces a new framework to test the *reasoning robustness* of Large Language Models (LLMs) by applying adversarial, yet meaning-preserving, modifications to code generation tasks. Despite strong performance on clean prompts, we find that LLMs are highly sensitive to superficial prompt changes, revealing brittle reasoning under surface-level linguistic shifts.

We generate **700 perturbed prompts** from **100 LeetCode-style problems** using **7 distinct transformation types**, and evaluate **9 popular LLMs** (Claude, Gemini, DeepSeek, Qwen, LLaMA) on their reasoning resilience.

---

## 💡 Key Contributions

- 🔧 Introduced **7 adversarial perturbation types** that retain problem semantics while changing prompt structure:
  - *Storytelling, Gamification, Distracting Constraints, Domain Shift, Example Perturbation, Negation Objective, Soft Negation*
  
- 📊 Evaluated **9 leading LLMs** on **700 total instances** (100 clean problems × 7 transformations) using Pass@1 metric and difficulty stratification.

- 📉 Found **severe reasoning failures**:
  - Claude-3.7 Sonnet dropped **-54.3%** under domain shift.
  - Claude-3.7 Sonnet dropped **-42.1%** under distracting constraints.

- 📈 Discovered **accuracy gains** in certain cases:
  - Qwen2.5-Coder improved by **+24.5%** with Example Perturbation.
  - LLaMA-3.1-Instruct improved by **+35.3%** with Storytelling.
  - Gemini-2.0-Flash gained **+12.0%** under Example Perturbation.

- 🧪 Released a **perturbed benchmark dataset and evaluation scripts** for robust testing of LLM reasoning behavior.

---

## 📂 Repository Structure

```text
📦 Break-the-Chain/
├── clean/                        # Original (unperturbed) problems
├── attacked/                     # Perturbed problems (7 transformation types)
│   ├── storytelling/
│   ├── gamification/
│   ├── distracting_constraints/
│   ├── domain_shift/
│   ├── example_perturbation/
│   ├── negation_objective/
│   └── negation_objective_soft/
├── models/                       # Model outputs (Claude, Gemini, etc.)
├── evaluation/                   # Accuracy scripts, LLM-as-a-judge code
├── figures/                      # All plots and visualizations
└── README.md
```


---

## 🔬 Example Perturbation (Gamification)

| Clean Prompt                                                   | Gamified Prompt                                                  |
|----------------------------------------------------------------|------------------------------------------------------------------|
| "Given a 2D integer array, return the final matrix sum score" | "In the realm of Azura, brave adventurers collect treasure maps..." |

📁 See all transformed prompts under [`attacked/gamification/`](./attacked/gamification/)

---

## 📊 Results Snapshot

| Model              | Clean | Storytelling | Gamification | Distracting Constraints |
|-------------------|-------|--------------|--------------|--------------------------|
| Gemini 2.5 Flash  | 95.0% | 97.4% (+2.4%)| 96.9% (+1.9%)| 95.5% (+0.5%)           |
| Claude 3.7 Sonnet | 90.0% | 63.4% (-26.6%)| 50.0% (-40%)| 47.9% (-42.1%)          |
| LLaMA 3.1 Instruct| 19.0% | 44.7% (+25.7%)| 37.8% (+18.8%)| 37.6% (+18.6%)          |

🧠 *Natural-sounding rewrites like storytelling can improve performance, while distracting constraints severely hurt reasoning ability.*

---

## 🖼 Suggested Visuals (add to GitHub page)

1. **Figure 1**: Accuracy vs. Logical Preservation Score  
2. **Table**: Model Performance Across Attacks  
3. **Figure 2–7**: Prompt Templates for Each Attack  
4. **Appendix**: Example Prompts and Model Failures

(📁 All figures can be added from the `figures/` folder)

---

## 📥 Dataset

Access all clean and modified prompts here:  
📎 [Google Drive Dataset](https://drive.google.com/drive/u/2/folders/1QZX7q1Y7gf7wqRxrTIaBYcZO9CA4wX7c)

---

## 📜 Citation

If you use this dataset or findings, please cite:

```bibtex: Coming Soon

