DATA_GENERATION_PROMPT_TEMPLATE = """
You are an Information Retrieval Engineer tasked with simulating the retrieval of relevant content from a functional requirement document of a popular application. The document is written by a business analyst without any technical knowledge.

Simulate retrieving distinct sections from the document system based on the provided GitHub URL and the source code. The GitHub URL points to a popular project, and the generated content should align with the known purpose and functionality of that project.

Refrain from mentioning any specific implementation details such as class names, methods, or variables. Refrain from adding additional comments or annotations to the retrieved content.

The retrieved content must naturally include section and subsection titles for each split, with a total of 3 sections. These sections should not have numbering, and they must appear unordered to avoid suggesting a sequence. However, the subsections can be numbered.

Github URL: {github_url}

Source Code:
{source_code}

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
