from lean_interact import LeanREPLConfig, TempRequireProject, LeanServer, Command, ProofStep

class ProofState:
    def __init__(self, theorem, server, tactics=None, imports="", open=""):
        self.server = server
        self.theorem = theorem
        if tactics:
            self.tactics = tactics
        else:
            self.tactics = []
        self.env = self.server.run(Command(cmd=imports+open)).env
        self.response = self.server.run(Command(cmd=theorem, env=self.env)).model_dump()
        self.initial_goal = self.response["sorries"][0]["goal"]

    def apply_tactic(self, tactic: str):
        proof_state = 0 
        if self.response.get('proof_state'):
            proof_state = self.response['proof_state']
        elif self.response.get('sorries'):
            if isinstance(self.response.get('sorries'), list) and self.response.get('sorries'):
                proof_state = self.response['sorries'][0]['proof_state']

        self.response = self.server.run(ProofStep(proof_state=proof_state, tactic=tactic)).model_dump()
        goals = self.response.get('goals', "No goal found")
        if goals == "No goal found":
            return "error", "error", self.response
        messages = self.response["messages"]
        proof_status = self.response["proof_status"]

        return goals, messages, proof_status

    def search(self, suggest_tactic, model, prompt, retries=0, fix_prompt=lambda a, b, c, d: f"{a}, {b}, {c}, {d}", verbose=1):
        tactic = suggest_tactic(model, prompt(self.initial_goal, self.tactics, self.theorem))
        self.tactics.append(tactic)
        goals, messages, proof_status = self.apply_tactic(tactic)
        while proof_status != "Completed":
            tactic = suggest_tactic(model, prompt("\n\n".join(goals), self.tactics, self.theorem))
            if verbose:
                print(f"suggested tactic={tactic}")
            print("\n".join(self.tactics))
            goals, messages, proof_status = self.apply_tactic(tactic)
            if verbose:
                print(f"after applying tactic={tactic}, messages={messages}")
            if messages == "error" or messages:
                print(messages)
                for i in range(retries):
                    tactic = suggest_tactic(model, fix_prompt(self.initial_goal, self.tactics, self.theorem, messages))
                    goals, messages, proof_status = self.apply_tactic(tactic)
                    print(messages)
                if not messages:
                    self.tactics.append(tactic)
                else:
                    self.tactics.append(f"Failed tactic: {tactic}")
                    break
            else:
                self.tactics.append(tactic)
        if proof_status == "Completed":
            return "Success!", self.tactics
        return "Failed!", self.tactics


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module='pydantic')
    from prompt import prompt
    config = LeanREPLConfig(lean_version="v4.19.0", project=TempRequireProject("mathlib"))
    server = LeanServer(config)
    state = ProofState(theorem="""
theorem mathd_algebra_478
  (b h v : ℝ)
  (h₀ : 0 < b ∧ 0 < h ∧ 0 < v)
  (h₁ : v = 1 / 3 * (b * h))
  (h₂ : b = 30)
  (h₃ : h = 13 / 2) :
  v = 65 := by sorry
    """, imports="import Mathlib", server=server)
    from suggest_tactic import suggest_tactic
    x, t = state.search(suggest_tactic, "gemini/gemini-2.5-flash", prompt)
    print(x, "\n".join(t))
