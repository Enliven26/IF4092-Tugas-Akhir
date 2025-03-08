# Introduction

AutoCommit is a library designed to generate commit messages using Large Language Models (LLM). It leverages high-level context information from the software project to create meaningful and accurate commit messages.

## Features

- **Commit Message Generation**: Automatically generate commit messages based on the changes in your codebase.
- **High-Level Context Awareness**: Utilize high-level context information from your project to enhance the quality of commit messages.
- **Integration with LLMs**: Leverage the power of Large Language Models to understand and describe code changes effectively.

## Installation
To install AutoCommit python library using pip, use the following command:

```sh
pip install git+https://github.com/Enliven26/IF4092-Tugas-Akhir.git@v[x].[y].[z]
```

## Evaluation
The `autocommit_evaluation` module is used to evaluate the performance of the AutoCommit library based on various metrics for research purposes. It helps in assessing the quality and accuracy of the generated commit messages by comparing them against a set of predefined criteria.

### Evaluation Metrics
- **Rationality**: The logical reasoning behind the code changes (explanation of "why").
- **Comprehensiveness**: The completeness of the summary related to the code changes (explanation of "what") and the coverage of every important detail.
- **Conciseness**: The brevity of the message to ensure quick readability and understanding.
- **Correctness**: The accuracy of the representation of code changes to ensure there is no incorrect, fabricated, or misleading information regarding the purpose, scope, or details of the code changes.

### Result
The result is available in the `src/autocommit_evaluation/data/result` folder.

### Reproduction
To reproduce the results, set the `.env` values based on the examples provided. Use the `scripts.ipynb` notebook inside the `src` folder to run the necessary scripts and evaluate the performance of the AutoCommit library.