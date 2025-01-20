import json
import requests
import os

# URL da API do Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"

# Caminho para o arquivo de memória
MEMORY_FILE = "memory.json"

# Função para carregar a memória do arquivo
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Erro ao carregar a memória: {e}")
            return {"interaction_history": []}
    return {"interaction_history": []}

# Função para salvar a memória no arquivo
def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w") as file:
            json.dump(memory, file, indent=4)
    except Exception as e:
        print(f"Erro ao salvar a memória: {e}")

# Função para gerar o contexto a partir da memória
def generate_context(memory, user_input):
    context = "Contexto da conversa:\n"
    for interaction in memory["interaction_history"]:  # Incluir todas as interações
        context += f"Usuário: {interaction['user']}\nLLaMA: {interaction['llama']}\n"
    context += f"Usuário: {user_input}\nLLaMA:"
    return context

# Função para gerar a resposta do modelo
def generate_response(prompt):
    payload = {
        "model": "llama3",  # Modelo LLaMA 3
        "prompt": prompt,
        "user_preferences": {
            "language": "pt"  # Preferência para o idioma português
        }
    }
    try:
        # Envia a solicitação para a API com streaming habilitado
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        response.raise_for_status()

        # Processa cada linha de JSON recebida
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                try:
                    json_line = json.loads(line)
                    full_response += json_line.get("response", "")
                except json.JSONDecodeError as e:
                    print(f"Erro ao processar linha JSON: {e}")

        return full_response if full_response else "Erro: Resposta inesperada do modelo."
    except requests.exceptions.RequestException as e:
        return f"Erro ao se comunicar com o modelo: {e}"

# Função principal de interação
def interact():
    print("Iniciando interação com LLaMA 3 via Ollama. Digite 'sair' para encerrar.")
    memory = load_memory()

    # Definir o nome do modelo como 'HAL' no início da conversa
    print("LLaMA: Eu sou HAL 9000, seu assistente pessoal!")

    while True:
        user_input = input("Você: ")
        if user_input.lower() == "sair":
            break

        # Gera o contexto com base no histórico de memória (todas as interações)
        prompt = generate_context(memory, user_input)
        response = generate_response(prompt)
        print(f"LLaMA: {response}")

        # Salva a interação na memória
        memory["interaction_history"].append({"user": user_input, "llama": response})
        save_memory(memory)

# Execução do programa
if __name__ == "__main__":
    interact()