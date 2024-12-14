DATA_GENERATION_PROMPT_TEMPLATE = """
You are an expert technical analyst and software architect. Below is a raw git diff string that contains changes in the codebase, along with the corresponding source code provided for additional context. Your task is to simulate searching for relevant content in the functional requirement document that directly corresponds to these changes.

Given the diff and the source code, identify what parts of a functional requirement document would describe or relate to these changes. Focus on:

The functionality or feature described by the diff and source code.
The purpose of the changes in terms of functional requirements.
Any specific sections, clauses, or requirements in the functional requirement document that the diff and source code might map to.
Avoid summarizing the diff or the source code themselves. Instead, simulate the process of retrieving and describing relevant sections of the functional requirement document in high-level detail.

Input Data:

Git Diff: 
{diff}

Source Code: 
{source_code}

Simulated Relevant Functional Requirement Document Content:
"""

LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """
{diff}
{source_code}
"""

HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """
{diff}
{context}
"""

DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE = """
Analyze the following source code and generate a concise query text that summarizes its functionality, purpose, and potential use cases. The query text should be suitable for retrieval tasks in the context of software development documentation, such as functional requirement documents or technical specifications.

Source Code:
{source_code}

Query Text Requirements:
1. Summarize the main functionality of the code in one or two sentences.
2. Focus on the high-level purpose of the code in the context of its application.
3. Avoid technical jargon unless necessary for clarity.

Query Text:
"""
