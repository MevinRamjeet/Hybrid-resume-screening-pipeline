from langchain_core.messages import SystemMessage, HumanMessage

# ================================
# 🔹 OpenAI (chat style)
# ================================
def openai_prompt_template(system_message: str, user_task: str):
    return [
        SystemMessage(content=system_message),
        HumanMessage(content=user_task),
    ]


# ================================
# 🔹 Qwen 1.5 / 2 Chat
# ================================
qwen_prompt_template = (
    """<|im_start|>system\n{system_message}\n<|im_end|>\n"""
    """<|im_start|>user\n{user_task}\n<|im_end|>\n"""
    """<|im_start|>assistant\n"""
)


# ================================
# 🔹 Gemma (base or IT)
# ================================
# Gemma-1/2 IT uses <start_of_turn>user etc.
gemma_prompt_template = (
    """<start_of_turn>system\n{system_message}<end_of_turn>\n"""
    """<start_of_turn>user\n{user_task}<end_of_turn>\n"""
    """<start_of_turn>model\n"""
)


# ================================
# 🔹 Mistral / LLaMA Instruct
# ================================
# Used by mistralai/Mistral-7B-Instruct-v0.2, Nous Hermes, etc.
mistral_prompt_template = (
    """[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n{user_task}\n[/INST]"""
)


# ================================
# 🔹 Vicuna / Alpaca / LLaMA-2 style
# ================================
vicuna_prompt_template = (
    """### System:\n{system_message}\n\n"""
    """### User:\n{user_task}\n\n"""
    """### Assistant:\n"""
)


# ================================
# 🔹 Zephyr / Tulu / Falcon-Instruct
# ================================
# Zephyr, Tulu, and Falcon-Instruct follow this lightweight style
zephyr_prompt_template = (
    """<|system|>\n{system_message}\n"""
    """<|user|>\n{user_task}\n"""
    """<|assistant|>\n"""
)