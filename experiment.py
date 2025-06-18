import gc
from lean_interact import LeanREPLConfig, TempRequireProject, LeanServer, Command, ProofStep

config = LeanREPLConfig(lean_version="v4.19.0", project=TempRequireProject("mathlib"))

tactics = ["linarith", "norm_num", "simp", "omega", "ring", "nlinarith"]

results = []
with open("minif2f/Test.lean", "r") as f:
    theorems = f.read().split("\n\n")
for theorem in theorems:
    server = LeanServer(config)
    response = server.run(Command(cmd="import Mathlib\n" + theorem))

    for tactic in tactics:
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

    del server
    gc.collect()

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
        
