# Analiza kodu: CRUD_operations.py

## Opis ogólny
Plik `CRUD_operations.py` implementuje podstawowe operacje CRUD (Create, Read, Update, Delete) dla bazy danych MongoDB (Azure Cosmos DB). Dodatkowo zawiera funkcje do mierzenia czasu wykonania operacji oraz wyszukiwania podobnych dokumentów na podstawie embeddingów.

## Szczegółowa analiza kodu

1. Importy i konfiguracja:
   ```python
   import time
   import pymongo
   from pymongo import MongoClient
   from pymongo.errors import ConnectionFailure, OperationFailure
   import numpy as np
   import dotenv
   import os

   dotenv.load_dotenv()
   COSMOSDB_CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")
   DB_NAME = os.environ.get("COSMOS_DB_NAME")
   COLLECTION_NAME = os.environ.get("COSMOS_COLLECTION_NAME")
   ```
   - Importowane są niezbędne moduły, w tym `time` do mierzenia czasu operacji i `numpy` do obliczeń na wektorach.
   - Ładowane są zmienne środowiskowe z pliku `.env`.

2. Funkcja `log_time`:
   ```python
   def log_time(operation_name, start_time, end_time):
       duration = end_time - start_time
       print(f"{operation_name} took {duration:.4f} seconds")
   ```
   - Funkcja pomocnicza do logowania czasu wykonania operacji.

3. Funkcja `connect_to_cosmosdb`:
   ```python
   def connect_to_cosmosdb(connection_string):
       start_time = time.time()
       try:
           client = MongoClient(connection_string)
           client.admin.command('ismaster')
           print("MongoDB connection established successfully.")
           return client
       except ConnectionFailure as e:
           print(f"MongoDB connection failed: {e}")
       except OperationFailure as e:
           print(f"MongoDB operation failed: {e}")
       finally:
           end_time = time.time()
           log_time("Connection", start_time, end_time)
       return None
   ```
   - Funkcja nawiązuje połączenie z bazą danych i mierzy czas tej operacji.
   - Obsługuje różne rodzaje błędów połączenia.

4. Funkcja `get_collection`:
   ```python
   def get_collection(client, db_name, collection_name):
       start_time = time.time()
       try:
           db = client[db_name]
           collection = db[collection_name]
           return collection
       except Exception as e:
           print(f"An error occurred while getting the collection: {e}")
           return None
       finally:
           end_time = time.time()
           log_time("Get Collection", start_time, end_time)
   ```
   - Funkcja pobiera określoną kolekcję z bazy danych.

5. Funkcje CRUD:
   - `insert_document(collection, document)`: Wstawia dokument do kolekcji.
   - `read_documents(collection, query)`: Odczytuje dokumenty z kolekcji na podstawie zapytania.
   - `update_document(collection, query, new_values)`: Aktualizuje dokument w kolekcji.
   - `delete_document(collection, query)`: Usuwa dokument z kolekcji.
   
   Każda z tych funkcji mierzy czas wykonania operacji i obsługuje potencjalne błędy.

6. Funkcje do wyszukiwania podobnych dokumentów:
   ```python
   def cosine_similarity(vec1, vec2):
       return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

   def find_similar_documents_v2(collection, query_vector):
       # ... (implementacja wyszukiwania podobnych dokumentów)

   def find_similar_documents(collection, embedding, threshold=0.9):
       # ... (alternatywna implementacja wyszukiwania podobnych dokumentów)
   ```
   - Funkcje te wykorzystują podobieństwo cosinusowe do wyszukiwania dokumentów podobnych do podanego wektora zapytania.

7. Główna część skryptu:
   ```python
   if __name__ == "__main__":
       # ... (kod testujący różne operacje CRUD i wyszukiwanie podobnych dokumentów)
   ```
   - Ta sekcja demonstruje użycie wszystkich zdefiniowanych funkcji, tworząc połączenie, wykonując operacje CRUD i wyszukując podobne dokumenty.

## Uwagi
- Kod zawiera dwie różne implementacje wyszukiwania podobnych dokumentów (`find_similar_documents_v2` i `find_similar_documents`), co może prowadzić do niejasności.
- Wszystkie operacje są opatrzone pomiarem czasu, co jest przydatne do celów debugowania i optymalizacji.
- Kod obsługuje błędy na poziomie każdej operacji, co zwiększa jego odporność.

## Potencjalne rozszerzenia
1. Dodanie bardziej zaawansowanych operacji, takich jak agregacje czy indeksowanie.
2. Implementacja systemu cachowania dla często wykonywanych zapytań.
3. Dodanie mechanizmu paginacji dla dużych zbiorów wyników.
4. Rozważenie użycia asynchronicznych operacji dla zwiększenia wydajności.
5. Implementacja systemu logowania do pliku zamiast wypisywania na konsolę.