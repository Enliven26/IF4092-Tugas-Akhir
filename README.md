python -m venv venv
.\venv\Scripts\activate
pip freeze > requirements.txt


$env:OLLAMA_DEBUG="1"
 & "ollama app.exe"