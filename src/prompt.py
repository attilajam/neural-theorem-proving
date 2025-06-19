prompt = lambda goal, tactics, theorem: f"""
[THM]
{theorem}
[/THM]
[STATE]
{goal}
[/STATE]
[TAC]
{"\n".join(tactics)}
... OUTPUT ONE SINGLE TACTIC TO BE PUT HERE
[/TAC]
"""
