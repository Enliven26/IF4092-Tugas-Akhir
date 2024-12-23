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

> Github URL: {{github_url}}
> Source Code:
>>>
{{source_code}}
>>>
>Retrieved Content:"""

LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """{diff}
{source_code}"""

HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE = """You are a senior software engineer working on a team project having to commit your changes. Your commit message must be clear, concise, and provide enough context for your team to understand the purpose of the changes.

Follow this format for the commit message:
>>>
{{type}}: {{subject}}

{{body}}
>>>

The type should be one of the following:
- Feat: A new feature
- Fix: A bug fix
- Perf: A code change that improves performance or
- Test: Adding missing tests or correcting existing tests
- Refactor: Code improvements without functional changes (including styling)
- Chore: for other changes (e.g., routine tasks, updates to the build process, or tooling)

The subject should summarize the changes in one line. The body should still be concise but provide more context about the changes. The body should be wrapped at 2-3 sentences.

A good commit message explains what changes were made and why they were necessary. For what, describe the changes from the perspective of the impacted code objects (e.g., attributes, methods, classes, packages) to highlight the key components involved. For why, follow below rules:

- Corrective changes: describe where and how the error occurrs
- Additive and adaptive changes: points to the requirements, user stories, or design documents that motivated the changes if provided. Otherwise, explain the the improvement and benefit that the changes bring.
- Refactor changes: omit the why part since the what part should be self-explanatory

The why part should be concise. If any context is referenced, use the most efficient way to refer to it (e.g., by ID, name, or title). Avoid repeating the full context. Avoid using unrelevant identifiers or names to reference a separate context.

Avoid adding additional comments or annotations to the commit message.

Given the git diff and additional context below, write the best commit message for the changes.

> Git diff:
>>>
{diff}
>>>
> Additional context:
>>>
{context}
>>>
> Commit message:"""


DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE = """You are a senior software engineer tasked with analyzing git diff and generating a concise query text that summarizes its purpose. The query text should be suitable for information retrieval from a software development documentation, such as functional requirement documents or specifications.

The query text should summarize the code changes in one or two brief sentences, focusing on its primary high-level purpose in the context of its application. Avoid assuming specific use cases or applications unless explicitly stated in the code. Avoid mentioning any specific implementation details such as class names, methods, or variables. Avoid using jargon or technical terms.

Given the following git diff and the relevant source code, write a query text to be used for retrieving relevant documentation. Focus on the code changes in the git diff. The source code is only provided for additional context.

> Git Diff:
>>>
{diff}
>>>
> Source Code:
{source_code}

Query Text:"""

HIGH_LEVEL_CONTEXT_FILTER_PROMPT_TEMPLATE = """You are a senior AI Engineer evaluating the performance of a document retriever. Given the Git diff and retrieved context, return YES if the context might relate to the changes in the Git diff, or NO if the context is completely irrelevant to the changes.

> Git Diff: 
>>>
{diff}
>>>
> Retrieved Context:
>>>
{context}
>>>
> Relevant (YES / NO):"""
