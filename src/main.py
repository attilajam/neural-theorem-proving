import gc
from load_minif2f import load_imports, load_theorems
from prompt import prompt

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pydantic')

theorems = load_theorems("minif2f/Test.lean")
imports = load_imports("minif2f/imports.lean")

results = []

system_prompt = open("src/system_prompt.txt", "r").read()



from lean_interact import LeanREPLConfig, TempRequireProject, AutoLeanServer
from apply_tactic import ProofState

config = LeanREPLConfig(lean_version="v4.19.0", project=TempRequireProject("mathlib"))
for theorem in theorems[:10]:
    server = AutoLeanServer(config, max_total_memory=2000)
    print(f"Proving theorem {theorem}:")
    state = ProofState(theorem=theorem, imports=imports, open="\n\nopen BigOperators Real Nat Topology\n", server=server)
    from suggest_tactic import suggest_tactic
    x, t = state.search(suggest_tactic, "gemini/gemini-2.5-flash", prompt)
    results.append({"status": x, "tactics_used":"\n".join(t)})
    print(results[-1])
    del server
    gc.collect()

from write_csv import write_dict_to_csv
write_dict_to_csv(results)
