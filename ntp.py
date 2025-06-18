from lean_interact import LeanREPLConfig, TempRequireProject, LeanServer, Command, ProofStep

import os
from dotenv import load_dotenv
load_dotenv()

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pydantic')
config = LeanREPLConfig(lean_version="v4.19.0", project=TempRequireProject("mathlib"))

results = []

with open("minif2f/Test.lean", "r") as f:
    theorems = f.read().split("\n\n")
with open("minif2f/imports.lean", "r") as f:
    imports = f.read()

server = LeanServer(config)
def tactic_suggest(theorem, goal):
    from litellm import completion

    os.environ["GEMINI_API_KEY"]
    messages = [{"content": f"Give a single tactic to continue proving the theorem {theorem} in Lean 4 with the goal state being: {goal}. Format your output as just plain text, don't use markdown code blocks or etc.", "role":"user"}]
    response = completion(model="gemini/gemini-2.0-flash", messages=messages)
    return response.choices[0].message.content

for theorem in theorems:
    print(f"Proving {theorem}")
    response = server.run(Command(cmd=imports+"\n\nopen BigOperators Real Nat Topology\n"+theorem))
    try:
        goal = response.model_dump()['sorries'][0]['goal']
    except:
        print(response.model_dump())
        break
    tactic = tactic_suggest(theorem, goal)
    print(tactic)
    response = server.run(ProofStep(tactic=tactic, proof_state=0))
    try:
        if response.has_errors():
            print("Has errors:", response.model_dump())
            continue
        else:
            d = response.model_dump()
            if d["proof_status"] == "Completed":
                results.append({"theorem":theorem, "tactic":tactic, "response":d})

    except:
        print("Failed", response.model_dump())

import csv

def write_dict_to_csv(data: list[dict], filename: str = 'output.csv'):
    if not data:
        print("The input data list is empty. No CSV file will be created.")
        return

    fieldnames = data[0].keys()

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for row_dict in data:
                writer.writerow(row_dict)
        print(f"Successfully wrote data to {filename}")
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

write_dict_to_csv(results)
        
