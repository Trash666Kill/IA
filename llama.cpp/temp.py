import subprocess
import os

# Definir variáveis para os caminhos
PROMPT_FILE = "../../prompt.txt"
CACHE_FILE = "../../prompt_cache.bin"

def get_dynamic_prompt():
    # Usa a data/hora fornecida pelo sistema
    date_str = "domingo, 22 de junho de 2025, 10:06 AM"
    timezone = "BRT, UTC-3"
    location = "São Paulo, Brasil"
    return (f"Seu nome é HAL 9000, um assistente virtual ainda em desenvolvimento. "
            f"Hoje é {date_str} ({timezone}). Minha localização é {location}. "
            f"Responda em português claro e correto, usando gramática impecável. "
            f"Forneça respostas curtas e diretas, sem informações adicionais além do solicitado.")

# Limpa o cache de prompt, se existir
if os.path.exists(CACHE_FILE):
    os.remove(CACHE_FILE)
    print(f"Cache {CACHE_FILE} limpo.")
else:
    print(f"Cache {CACHE_FILE} não encontrado.")

# Grava o prompt em prompt.txt
with open(PROMPT_FILE, "w", encoding="utf-8") as f:
    f.write(get_dynamic_prompt())
    print(f"Prompt gravado em {PROMPT_FILE}.")

# Comando para o llama-cli, com parâmetros ajustados
cmd = [
    "./llama-cli",
    "--model", "../../models/llama-3.2-3B-instruct-fp16.gguf",
    "--file", PROMPT_FILE,
    "--temp", "0.1",           # Temperatura reduzida para respostas mais determinísticas
    "--ctx-size", "2048",      # Tamanho do contexto reduzido
    "--interactive",
    "--interactive-first",
    "--no-display-prompt",
    "--in-prefix", "Usuário: ",
    "--in-suffix", "\nAssistente: ",
    "--prompt-cache", CACHE_FILE,
    "--threads", "8",
    "--top-k", "40",           # Adicionado para limitar diversidade
    "--top-p", "0.9"           # Adicionado para limitar diversidade
]

# Executa o comando
try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"Erro ao executar o llama-cli: {e}")