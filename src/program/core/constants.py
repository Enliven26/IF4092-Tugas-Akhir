DATA_GENERATION_PROMPT_TEMPLATE = """
You are an expert technical analyst and software architect. Below is a raw git diff string that contains changes 
in the codebase. Your task is to simulate searching for relevant content in the functional requirement document 
that directly corresponds to these changes.

Given the diff, identify what parts of a functional requirement document would describe or relate to these changes. 
Focus on:
1. The functionality or feature described by the diff.
2. The purpose of the changes in terms of functional requirements.
3. Any specific sections, clauses, or requirements in the functional requirement document that the diff might map to.

You should refrain from summarizing the diff itself. Instead, simulate the process of retrieving relevant parts of the functional 
requirement document and describe them in high-level detail.

Git Diff:
{diff}

Source Code:
{source_code}

Simulated Relevant Functional Requirement Document Content:
"""

LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """
{diff}
"""

HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """
{diff}
{context}
"""

DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE = """
{source_code}
"""
