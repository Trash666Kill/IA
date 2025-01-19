import requests
import json
import os

# Função para carregar um arquivo JSON
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Função para salvar um dicionário como JSON
def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Função para enviar o prompt ao Ollama
def send_to_ollama(prompt, config):
    url = config.get("ollama_url", "http://localhost:11434/api/generate")
    model = config.get("model", "llama3.2")

    payload = {"model": model, "prompt": prompt}

    try:
        # Realiza a requisição ao Ollama com streaming
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        # Processa os dados de streaming JSON
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    full_response += data.get("response", "")
                except json.JSONDecodeError:
                    continue

        return full_response or "[Erro: Nenhuma resposta do modelo.]"

    except requests.exceptions.RequestException as e:
        return f"[Erro ao conectar ao Ollama: {e}]"

# Função principal para interação
def main():
    # Carrega configurações e memória
    config = load_json("config.json")
    memory = load_json("memory.json")

    print("Iniciando interação. Digite 'sair' para encerrar.")
    print("LLaMA (Formal, Português (Brasil)): Olá, estou pronto para conversar com você!")

    while True:
        user_input = input("Você: ")
        if user_input.lower() == "sair":
            print("LLaMA: Até logo!")
            break

        # Adiciona ao histórico de memória
        memory.setdefault("interactions", []).append({"user": user_input})

        # Envia o prompt ao Ollama
        response = send_to_ollama(user_input, config)
        print(f"LLaMA: {response}")

        # Salva a resposta na memória
        memory["interactions"][-1]["llama"] = response

        # Atualiza o arquivo de memória
        save_json("memory.json", memory)


if __name__ == "__main__":
    main()