from lean_interact import LeanREPLConfig, TempRequireProject, LeanServer, Command, ProofStep

import os
from dotenv import load_dotenv
load_dotenv()

# Ignores warning from Pydantic -- caused by a bug with litellm
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pydantic')

config = LeanREPLConfig(lean_version="v4.19.0", project=TempRequireProject("mathlib"))

results = []

with open("minif2f/Test.lean", "r") as f:
    theorems = f.read().split("\n\n")
with open("minif2f/imports.lean", "r") as f:
    imports = f.read()

server = LeanServer(config)
system_prompt = """
You are proving a theorem in Lean 4.
You are given the following information:
- The theorem you are proving, inside [THM]...[/THM]
- The current proof state, inside [STATE]...[/STATE]
- The previous tactics that were used to get to that state if any, inside [TAC]...[/TAC]
Your task is to generate the next tactic in the proof. Provide just a single tactic, for example:
[STATE]⊢ ∀ n > 0, 5 ^ n > n.factorial ↔ n ≤ 11[/STATE]
[TAC]
intro n hn_pos
apply Iff.intro
intro h_pow_gt_fact
[/TAC]

You would output:
contrapose! h_pow_gt_fact

No markdown styling like (` around the code `), a single line of Lean 4 code, with only one tactic to run. 
"""

def tactic_suggest(model, prompt):
    from litellm import completion

    os.environ["GEMINI_API_KEY"]
    messages = [{"role":"system", "content": system_prompt}, {"content": prompt, "role":"user"}]
    response = completion(model=model, messages=messages)
    return response.choices[0].message.content


for theorem in theorems:
    print(f"Proving {theorem}")
    tactics = []
    response = server.run(Command(cmd=imports+"\n\nopen BigOperators Real Nat Topology\n"+theorem))
    while True:
        d = response.model_dump()
        if d.get('sorries'):
            goal = d['sorries'][0]['goal']
            print(f"Current goal state {goal}")
        elif d.get('goals'):
            goal = "\n".join(d['goals'])
            print(goal)
        else:
            print(response.model_dump())
            break

        tactic = tactic_suggest("gemini/gemini-2.5-flash", prompt(goal, tactics, theorem))
        print("LLM suggests", tactic)
        response = server.run(ProofStep(tactic=tactic, proof_state=0))
        try:
            if response.has_errors():
                print("Has errors:", response.model_dump())
                continue
            else:
                tactics.append(tactic)
                d = response.model_dump()
                if d["proof_status"] == "Completed":
                    results.append({"theorem":theorem, "tactic":tactic, "response":d})
                    break
        except:
            print(response.model_dump())
            break
    # for theorem in theorems:
    #     print(f"Proving {theorem}")
    #     tactics = []
    #     response = server.run(Command(cmd=imports+"\n\nopen BigOperators Real Nat Topology\n"+theorem))
    #     try:
    #         goal = response.model_dump()['sorries'][0]['goal']
    #     except:
    #         print(response.model_dump())
    #         break
    #     tactic = tactic_suggest("gemini/gemini-2.5-flash-lite-preview-06-17", prompt(goal, tactics, theorem))
    #     print(tactic)
    #     response = server.run(ProofStep(tactic=tactic, proof_state=0))
    #     while True:
    #         try:
    #             if response.has_errors():
    #                 print("Has errors:", response.model_dump())
    #                 continue
    #             else:
    #                 tactics.append(tactic)
    #                 d = response.model_dump()
    #                 if d["proof_status"] == "Completed":
    #                     results.append({"theorem":theorem, "tactic":tactic, "response":d})
    #                     break
    # 
    #                 try:
    #                     goal = d['sorries'][0]['goal']
    #                 except:
    #                     print(d)
    #                     break
    #                 print(d, "\n", goal)
    #                 tactic = tactic_suggest("gemini/gemini-2.5-flash-lite-preview-06-17", prompt(goal, tactics, theorem))
    #                 print(tactic)
    #                 response = server.run(ProofStep(tactic=tactic, proof_state=0))
    #                 
    #         except:
    #             print("Failed", response.model_dump())
    #             break


write_dict_to_csv(results)
        
