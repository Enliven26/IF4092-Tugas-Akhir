DATA_GENERATION_PROMPT_TEMPLATE = """
You are an Information Retrieval Engineer tasked with simulating the retrieval of relevant content from a functional requirement document. The document system may return content that is scattered across multiple sections or splits.

Simulate retrieving 3 distinct splits from the document system. Each section should include high-level explanations of the requirements. Refrain from delving into specific implementation details such as class names, methods, or variables. Refrain from adding additional comments or annotations to the retrieved content.

The retrieved content must include section and subsections titles for each split. The splits should appear unordered to avoid a structured or sequential appearance. Avoid using --- to separate the splits.

Source Code: {source_code}

Retrieved Content:
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
You are a senior software engineer tasked with analyzing source code and generating a concise query text that summarizes its functionality and purpose. The query text should be suitable for retrieval tasks in the context of software development documentation, such as functional requirement documents or technical specifications.

The query text should summarize the main functionality of the code in one or two sentences, focusing on its high-level purpose in the context of its application. Avoid assuming specific use cases or applications unless explicitly stated in the code, and refrain from using technical jargon unless it is necessary for clarity. 

Source Code:
{source_code}

Query Text:
"""
