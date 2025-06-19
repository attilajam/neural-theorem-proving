import os

def suggest_tactic(model, prompt):
    from litellm import completion
    system_prompt = open("src/system_prompt.txt", "r").read()
    os.environ["GEMINI_API_KEY"]
    messages = [{"role":"system", "content":system_prompt}, {"role":"user", "content":prompt}]
    response = completion(model=model, messages=messages, max_tokens=20, thinking={"type": "enabled", "budget_tokens": 100})
    return response.choices[0].message.content

    
