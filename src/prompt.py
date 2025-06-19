prompt = lambda goal, tactics, theorem: f"""
Here is the given state information, your task is to provide the next tactic.
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
