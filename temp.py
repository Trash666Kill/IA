import json
import requests
import os

# URL da API de Pesquisa Personalizada do Google
GOOGLE_API_URL = "https://www.googleapis.com/customsearch/v1"

# Sua chave de API do Google e o ID do mecanismo de pesquisa
API_KEY = "SUA_CHAVE_DE_API"
CX = "SEU_ID_DO_MECANISMO_DE_PESQUISA"

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

# Função para realizar a pesquisa no Google
def google_search(query):
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
    }
    try:
        response = requests.get(GOOGLE_API_URL, params=params)
        response.raise_for_status()
        search_results = response.json()

        if "items" in search_results:
            # Exibe os primeiros 3 resultados
            results = ""
            for item in search_results["items"][:3]:
                results += f"{item['title']}: {item['link']}\n"
            return results
        else:
            return "Nenhum resultado encontrado."
    except requests.exceptions.RequestException as e:
        return f"Erro ao buscar na web: {e}"

# Função principal de interação
def interact():
    print("Iniciando interação com pesquisa na web. Digite 'sair' para encerrar.")
    memory = load_memory()

    # Definir o nome do assistente
    print("Assistente: Olá, estou pronto para fazer pesquisas na web para você!")

    while True:
        user_input = input("Você: ")
        if user_input.lower() == "sair":
            break

        # Gera o contexto com base no histórico de memória (todas as interações)
        prompt = generate_context(memory, user_input)

        # Realiza a pesquisa no Google
        response = google_search(user_input)
        print(f"Assistente: {response}")

        # Salva a interação na memória
        memory["interaction_history"].append({"user": user_input, "llama": response})
        save_memory(memory)

# Execução do programa
if __name__ == "__main__":
    interact()
