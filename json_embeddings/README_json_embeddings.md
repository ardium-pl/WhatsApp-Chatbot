# Rozszerzony przegląd folderu: json_embeddings

## Cel folderu
Folder json_embeddings zawiera kod i pliki konfiguracyjne służące do generowania embeddings dla danych tekstowych z plików JSON przy użyciu modelu OpenAI. Celem jest przetworzenie tekstu na wektory numeryczne, które mogą być wykorzystane w zadaniach przetwarzania języka naturalnego.

## Kluczowe pliki i ich funkcje

1. **embeddings_ada_002.py**
   - Główny skrypt do generowania embeddings.
   - Kluczowe importy i konfiguracja:
     ```python
     import os
     import json
     import dotenv
     from typing import List, Dict, Any
     from openai import OpenAI

     dotenv.load_dotenv()
     OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
     client = OpenAI(api_key=OPENAI_API_KEY)
     ```
   - Najważniejsze funkcje:
     ```python
     def generate_embedding(text: str) -> List[float]:
         response = client.embeddings.create(
             model="text-embedding-ada-002",
             input=text
         )
         return response.data[0].embedding

     def add_embeddings_to_json(data: Dict[str, Any]) -> Dict[str, Any]:
         vectors = []
         for page in data.get("pages", []):
             for _, content in page.items():
                 embedding = generate_embedding(content)
                 vectors.append(embedding)
         data["vectors"] = vectors
         return data
     ```
   - Obsługa błędów i logowanie:
     ```python
     try:
         # kod generujący embedding
     except Exception as e:
         print(f"Error generating embedding: {e}")
     ```

2. **.env i .env.example**
   - Pliki konfiguracyjne do przechowywania zmiennych środowiskowych.
   - Kluczowe zmienne:
     ```
     OPEN_AI_KEY="your_open_ai_key_here"
     INPUT_PATH_FILE="path_to_your_input_file_here"
     COSMOSDB_CONNECTION_STRING="your_cosmosdb_connection_string_here"
     DB_NAME="your_database_name_here"
     COSMOS_COLLECTION_NAME="your_collection_name_here"
     ```

3. **output_test.json**
   - Przykładowy plik wejściowy/wyjściowy JSON.
   - Rozszerzona struktura z przykładowymi danymi:
     ```json
     {
       "pages": [
         {
           "Page 1": "Euvic Services.\n►►►►►►►►►►►\nEUVIC_The GoodPeople\nPrezentacja kluczowych kompetencji\n"
         },
         {
           "Page 2": "„Klienci nie są najważniejsi. \nPracownicy są najważniejsi.\n \nJeżeli zadbasz o swoich pracowników, \noni zatroszczą się o klientów"\nRichard Branson\n"
         }
       ]
     }
     ```

## Szczegółowy przepływ pracy
1. Ładowanie zmiennych środowiskowych z pliku `.env`.
2. Inicjalizacja klienta OpenAI z kluczem API.
3. Wczytanie danych z pliku JSON określonego w `INPUT_PATH_FILE`:
   ```python
   input_json_path = os.getenv("INPUT_PATH_FILE")
   data = load_json(input_json_path)
   ```
4. Iteracja przez strony w danych i generowanie embeddings dla każdej strony:
   ```python
   for page in data.get("pages", []):
       for _, content in page.items():
           embedding = generate_embedding(content)
           vectors.append(embedding)
   ```
5. Dodanie wygenerowanych embeddings do oryginalnej struktury JSON jako nowa lista "vectors".
6. Zapisanie wynikowego JSON z embeddingami do pliku `output_with_embeddings.json`:
   ```python
   save_json(data_with_embeddings, 'output_with_embeddings.json')
   ```

## Kluczowe aspekty techniczne
- Wykorzystanie modelu "text-embedding-ada-002" od OpenAI, który generuje embeddingi o wymiarze 1536.
- Asynchroniczne wywołania API OpenAI nie są implementowane, co może wpływać na wydajność przy dużych zbiorach danych.
- Obsługa błędów obejmuje problemy z połączeniem API, nieprawidłowe formaty JSON i brakujące pliki.

## Potencjalne zastosowania i rozszerzenia
- Wyszukiwanie semantyczne w bazie dokumentów.
- Klasyfikacja i grupowanie dokumentów na podstawie podobieństwa treści.
- Możliwość rozszerzenia o funkcje porównywania embeddings, np. przy użyciu podobieństwa kosinusowego.

## Uwagi dotyczące wydajności i skalowalności
- Proces może być czasochłonny dla dużych zestawów danych ze względu na ograniczenia API OpenAI.
- Przy dużych plikach wejściowych należy rozważyć przetwarzanie wsadowe lub implementację mechanizmu wznawiania w przypadku przerwania.
- Aktualnie brak mechanizmów cachowania wyników, co mogłoby przyspieszyć przetwarzanie powtarzających się treści.

## Bezpieczeństwo i zarządzanie danymi
- Klucz API OpenAI jest przechowywany w zmiennych środowiskowych, co jest dobrą praktyką bezpieczeństwa.
- Należy zwrócić uwagę na potencjalne wycieki danych przy przesyłaniu treści do API OpenAI.
- Brak implementacji szyfrowania danych w spoczynku dla plików wyjściowych zawierających embeddingi.