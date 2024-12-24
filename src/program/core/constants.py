RANDOM_REQUIREMENT_ID_FORMATS = [
    "REQ-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "USERSTORY-{{STORY_NAME}}-{{SECTION_NUMBER}}",
    "{{TASK_NAME}}-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "GOAL-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "MILESTONE-{{MILESTONE_NAME}}-{{SECTION_NUMBER}}",
    "DELIVERABLE-{{DELIVERABLE_NAME}}-{{SECTION_NUMBER}}",
    "EPIC-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "{{PROJECT_NAME}}-USERREQ-{{SECTION_NUMBER}}",
    "SCOPE-{{SCOPE_NAME}}-{{SECTION_NUMBER}}",
    "OBJ-{{OBJECTIVE_NAME}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "{{TASK_NAME}}-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "REQ-{{RANDOM_WORD}}-{{SECTION_NUMBER}}",
    "SCOPE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "STORY-{{STORY_NAME}}-{{SECTION_NUMBER}}",
    "OBJECTIVE-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "USER-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "DELIVERABLE-{{DELIVERABLE_TYPE}}-{{SECTION_NUMBER}}",
    "TASK-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "PROJECT-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "USER-{{USER_NAME}}-{{SECTION_NUMBER}}",
    "DELIVERABLE-{{DELIVERABLE_NAME}}-{{SECTION_NUMBER}}",
    "PROJECT-{{PROJECT_CODE}}-{{SECTION_NUMBER}}",
    "GOAL-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "USERSTORY-{{USERSTORY_NAME}}-{{SECTION_NUMBER}}",
    "MILESTONE-{{MILESTONE_NAME}}-{{SECTION_NUMBER}}",
    "OBJ-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "FEATURE-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "{{TASK_NAME}}-{{PROJECT_NAME}}-{{SECTION_NUMBER}}",
    "TASK-{{RANDOM_SEQUENCE}}-{{SECTION_NUMBER}}",
]

END_DOCUMENT_SPLIT_SEPARATOR = "\n\n--- RETRIEVED DOCUMENT SPLIT END ---\n\n"

DATA_GENERATION_PROMPT_TEMPLATE = f"""You are an Information Retrieval Engineer tasked with simulating the retrieval of relevant content from a functional requirement document of a popular application. The document is written by a business analyst without any technical knowledge.

The retrieved content should contain {{section_count}} sections, each representing a distinct user requirement. Each section must include a unique identifier for the requirement, following the format: {{requirement_id_format}}, with the placeholder replaced by the actual values relevant to the requirement. Use section numbering in the specific order: {{section_order_string}}. Each section should have some subsections that provide detailed explanations of the requirement. At the end of each section, include the separator: {END_DOCUMENT_SPLIT_SEPARATOR}

Avoid mentioning any specific implementation details such as class names, methods, or variables. Avoid adding additional comments or annotations to the retrieved content.

Simulate retrieving distinct sections from the document system based on the provided GitHub URL and the source code. The GitHub URL points to a popular project, and the generated content should align with the known purpose and functionality of that project.

Github URL: {{github_url}}
Source Code:
{{source_code}}

Retrieved Content:"""

LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """{diff}
{source_code}"""

HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """Write a concise commit message based on the Git diff and additional context provided. If the context is relevant, include it in the commit body. Use IDs, names, or titles for brevity, and referencing multiple contexts is allowed. Focus on the most relevant contexts.

A good commit message explains what changes were made and why they were necessary. Wrap the body at one to three brief sentences. Avoid adding additional comments or annotations to the commit message.

Follow this format for the commit message:

{{type}}: {{subject}}

{{body}}

The type should be one of the following: feat, fix, perf, test, refactor, or chore. If any of these types are not suitable, use chore as default.

Git diff:
{diff}

Additional context:
{context}

Commit message:"""


DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE = """Given a Git diff and the relevant source code, write a concise summary of the code changes in a way that a non-technical person can understand. The query text must summarize the code changes in two very brief sentences.

Git diff:
{diff}

Source code:
{source_code}

Query text:"""

HIGH_LEVEL_CONTEXT_FILTER_PROMPT_TEMPLATE = """Evaluate the performance of a document retriever. Given the Git diff and retrieved context, return YES if the context directly or indirectly correlates with the changes in the Git diff. Otherwise, return NO.

> Git diff: 
>>>
{diff}
>>>
> Retrieved context:
>>>
{context}
>>>
> Relevant (YES / NO):"""
