from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ===== استخدام نموذج Bloom متوسط الحجم =====
model_name = "bigscience/bloom-560m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_bot_message(prompt, max_length=100):
    """
    توليد رسالة تفاعلية للمستخدم باستخدام Bloom 560M
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            inputs['input_ids'],
            max_length=max_length,
            do_sample=True,
            top_p=0.9,
            temperature=0.8
        )
    message = tokenizer.decode(outputs[0], skip_special_tokens=True)
    message = message.replace(prompt, "").strip()
    return message
