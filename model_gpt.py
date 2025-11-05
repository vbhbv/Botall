from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# تحميل نموذج محادثة صغير من مايكروسوفت
model_name = "microsoft/DialoGPT-small"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

chat_history_ids = None  # لحفظ المحادثة القصيرة

def generate_bot_message(prompt: str, max_length: int = 100) -> str:
    """
    توليد رد ذكي وسريع باستخدام DialoGPT-small
    """
    global chat_history_ids

    # تحويل النص إلى توكنز
    new_input_ids = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt")

    # توليد الرد اعتماداً على التاريخ
    bot_output = model.generate(
        torch.cat([chat_history_ids, new_input_ids], dim=-1) if chat_history_ids is not None else new_input_ids,
        max_length=max_length,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_p=0.9,
        temperature=0.8,
    )

    chat_history_ids = bot_output  # حفظ التاريخ للرد التالي

    reply = tokenizer.decode(bot_output[:, new_input_ids.shape[-1]:][0], skip_special_tokens=True)

    # تحسين الرد قليلاً
    if reply.strip() == "":
        reply = "أنا هنا أساعدك في تحميل الفيديوهات 🎬، أرسل الرابط فقط!"
    elif len(reply) > 200:
        reply = reply[:200] + "..."

    return reply
