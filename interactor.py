import json
import requests
import os

# URL da API do Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"

# Caminho para o arquivo de memória
MEMORY_FILE = "memory.json"

# Controle do log do payload
ENABLE_PAYLOAD_LOG = False

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
    for interaction in memory["interaction_history"]:
        context += f"Usuário: {interaction['user']}\nLLaMA: {interaction['llama']}\n"
    context += f"Usuário: {user_input}\nLLaMA:"
    return context

# Função para salvar a interação somente se não for repetitiva
def save_interaction(memory, user_input, llama_response):
    if memory["interaction_history"] and memory["interaction_history"][-1]["llama"] == llama_response:
        print("Resposta repetitiva detectada, interação não será salva.")
        return
    memory["interaction_history"].append({"user": user_input, "llama": llama_response})
    save_memory(memory)

# Função para gerar a resposta do modelo
def generate_response(prompt):
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "user_preferences": {
            "language": "pt"
        }
    }

    # Exibir o payload somente se habilitado
    if ENABLE_PAYLOAD_LOG:
        print("\n=== Payload enviado ===")
        print(json.dumps(payload, indent=4, ensure_ascii=False))
        print("=======================\n")

    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        response.raise_for_status()

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
    print("Iniciando interação com LLaMA 3.2 via Ollama. Digite 'sair' para encerrar.")
    memory = load_memory()

    print("LLaMA: Eu sou HAL 9000, seu assistente pessoal!")

    while True:
        user_input = input("Você: ")
        if user_input.lower() == "sair":
            break

        prompt = generate_context(memory, user_input)
        response = generate_response(prompt)
        print(f"LLaMA: {response}")

        save_interaction(memory, user_input, response)

# Execução do programa
if __name__ == "__main__":
    interact()