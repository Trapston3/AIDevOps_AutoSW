# AIDD-Unit-2-24BTRAO034-RejuthaSreeM

## Expense Splitter

A small Python application for recording shared expenses and splitting costs among participants.

## Project Description

Expense Splitter helps users manage shared expenses by recording expenses, calculating totals, and determining how much each participant owes.

## Features

- Record shared expenses
- Store expense descriptions and amounts
- Track who paid for an expense
- Track participants sharing an expense
- Calculate total expenses
- Calculate expenses associated with a participant
- Split expenses equally among participants
- Handle rounding correctly during equal splits
- Unit tests using pytest

## Project Structure

```text
AIDD-Unit-2-24BTRAO034-RejuthaSreeM/
│
├── expense_splitter/
│   ├── __init__.py
│   └── models.py
│
├── tests/
│   └── test_models.py
│
├── requirements.txt
├── pytest.ini
└── README.md
```

## Requirements

- Python 3.x
- pytest

## Setup

### Clone the Repository

```bash
git clone https://github.com/RejuthaSree/AIDD-Unit-2-24BTRAO034-RejuthaSreeM.git
```

### Navigate to the Project Folder

```bash
cd AIDD-Unit-2-24BTRAO034-RejuthaSreeM
```

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Virtual Environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Tests

Run all unit tests using:

```bash
pytest
```

## AI Coding Tool Used

**Cursor AI — Free Hobby Tier**

Cursor was used as the AI-powered coding assistant for developing, testing, and debugging this project.

## Prompting Techniques Used

### Zero-shot Prompting

Zero-shot prompting was used for well-defined tasks such as generating the initial project structure and implementing the core Expense Splitter functionality.

### Few-shot Prompting

Few-shot prompting was used to maintain consistent project conventions, including documentation and test styles. Examples were provided in the prompt so that Cursor could follow the desired format consistently.

### Chain-of-Thought Prompting

Chain-of-thought prompting was used to debug a non-trivial rounding edge case when splitting an expense equally among participants. The AI was instructed to "think step by step" to identify the cause of the problem and provide a correct solution.

## Testing

The project includes unit tests written using pytest.

The tests verify:

- Expense creation
- Expense validation
- Adding expenses
- Calculating total expenses
- Finding expenses associated with a participant
- Equal expense splitting
- Correct handling of rounding edge cases

## Assignment

This project was created for:

**Automation in Software Development**

**Assignment 1**

## Repository Documentation

The repository documentation includes:

- Prompt logs for the AI interactions
- Evidence of zero-shot prompting
- Evidence of few-shot prompting
- Evidence of chain-of-thought prompting
- Screenshots of Cursor interactions
- A reflection comparing Cursor with GitHub Copilot