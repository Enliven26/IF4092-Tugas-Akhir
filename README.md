python -m venv venv
.\venv\Scripts\activate
pip freeze > requirements.txt


$env:OLLAMA_DEBUG="1"
 & "ollama app.exe"

windows-R + explorer %LOCALAPPDATA%\Ollama

https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md#how-to-troubleshoot-issues