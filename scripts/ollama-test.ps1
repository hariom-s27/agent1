# Quick Ollama smoke test using the configured model
Get-Content .env | Write-Output

# show installed models
ollama list

# run a short prompt
ollama run $env:SIDEKICK_ACT_MODEL "Say hello and confirm model name." 
