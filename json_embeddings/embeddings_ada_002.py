import os
import json
import dotenv
from typing import List, Dict, Any
from openai import OpenAI

# Wczytaj zmienne środowiskowe
dotenv.load_dotenv()

# Pobierz klucz API z zmiennej środowiskowej
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Nie znaleziono klucza API OpenAI. Proszę ustawić zmienną środowiskową OPEN_AI_KEY.")

# Zainicjuj klienta OpenAI z kluczem API
client = OpenAI(api_key=OPENAI_API_KEY)

# Ustaw ścieżkę do głównego folderu output
OUTPUT_FOLDER = r"C:\Users\szyme\to_be_parsed\output"
if not os.path.exists(OUTPUT_FOLDER):
    raise ValueError(f"Nie znaleziono folderu output: {OUTPUT_FOLDER}")


def generate_embedding(text: str) -> List[float]:
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Błąd generowania embeddingu: {e}")
        return []


def load_json(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Nie znaleziono pliku: {file_path}")
        return {"pages": []}
    except json.JSONDecodeError:
        print(f"Nieprawidłowy JSON w pliku: {file_path}")
        return {"pages": []}


def save_json(data: Dict[str, Any], file_path: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def add_embeddings_to_json(data: Dict[str, Any]) -> Dict[str, Any]:
    vectors = []
    for page in data.get("pages", []):
        for page_num, content in page.items():
            embedding = generate_embedding(content)
            vectors.append(embedding)

    data["vectors"] = vectors
    return data


def process_folder(input_folder: str, output_folder: str) -> None:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"embedded_{filename}")

            print(f"Przetwarzanie pliku: {filename}")
            data = load_json(input_path)
            data_with_embeddings = add_embeddings_to_json(data)
            save_json(data_with_embeddings, output_path)
            print(f"Zapisano plik z embeddingami: {output_path}")


def main():
    subfolders = ["pdf", "pptx"]
    embeddings_folder = os.path.join(OUTPUT_FOLDER, "embeddings")

    for subfolder in subfolders:
        input_folder = os.path.join(OUTPUT_FOLDER, subfolder)
        if os.path.exists(input_folder):
            output_subfolder = os.path.join(embeddings_folder, subfolder)
            process_folder(input_folder, output_subfolder)
        else:
            print(f"Folder {subfolder} nie istnieje w {OUTPUT_FOLDER}")

    print("Dodano embeddingi do wszystkich plików JSON i zapisano w folderze wyjściowym.")


if __name__ == "__main__":
    main()