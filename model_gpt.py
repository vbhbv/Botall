from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ===== تحميل نموذج GPT صغير =====
model_name = "EleutherAI/gpt-neo-125M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_bot_message(prompt, max_length=50):
    """
    توليد رسالة تفاعلية للمستخدم باستخدام GPT صغير
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(inputs['input_ids'], max_length=max_length, do_sample=True, top_p=0.9)
    message = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # إزالة النص الأصلي من الرد
    message = message.replace(prompt, "").strip()
    return message
