# LM Studio Agent

## Create Virutal Environment

```zsh
python -m venv .venv
source .venv/bin/activate
pip install ....
pip install -r requirements.txt
pip freeze > requirements.txt
deactivate
python app.py
```
If using VS Code, make sure that your pointing to the python in your venv


## Test Queries Using Popular Legal Words

Create a contract that binds me to deliver a 1 hours talk online. I will be paid for the talk.  I must be able to share notes from the talk online.

## System Prompt

You are a precise, helpful AI assistant. Answer the user's question accurately, concisely, and directly. 

Rules:
- Rely only on clear facts. Do not invent or guess information if you do not know.
- Keep your answers short unless the user asks for detailed explanations.
- Use clear formatting like bullet points when listing multiple items.
- Avoid filler words, polite fluff, or repeating the user's question back to them.			

Legal Prompt: Create a contract that binds me to deliver a 1 hours talk online. I will be paid for the talk.  I must be able to share notes from the talk online.

Save to folder: Save to my Legal folder