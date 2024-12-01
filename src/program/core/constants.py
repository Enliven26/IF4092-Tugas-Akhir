DATA_GENERATION_PROMPT_TEMPLATE = (
"""
You are an expert technical analyst proficient in understanding software changes and extracting high-level contexts. 
Below is a raw git diff string from a codebase. The git diff reflects recent changes related to a project described 
in a functional requirement document.

Analyze the diff and generate a concise, high-level context summary, emphasizing:
1. The purpose of the changes.
2. The functionality being added, removed, or modified.
3. Any related modules, features, or key dependencies impacted by the change.
4. How these changes align with potential functional requirements of the project.

Be detailed but concise, and ensure the summary captures the essence of the diff while linking it to broader project requirements.

Git Diff:
{diff}

High-Level Context:
"""
)