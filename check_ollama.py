import ollama
try:
    print(ollama.list())
except Exception as e:
    print(e)
