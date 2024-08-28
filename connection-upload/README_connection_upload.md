# Folder: connection_upload

## Opis
Folder "connection_upload" zawiera pliki związane z połączeniem do bazy danych MongoDB (Azure Cosmos DB) oraz implementacją operacji CRUD (Create, Read, Update, Delete). Dodatkowo, zawiera on dwa interfejsy graficzne (GUI) do zarządzania bazą danych.

## Zawartość folderu

### 1. .env.example
Plik zawierający przykładowe zmienne środowiskowe potrzebne do konfiguracji połączenia z bazą danych i innymi usługami.

Kluczowe zmienne:
- `COSMOSDB_CONNECTION_STRING`: String połączenia do Azure Cosmos DB
- `DB_NAME`: Nazwa bazy danych
- `COSMOS_COLLECTION_NAME`: Nazwa kolekcji w bazie danych
- `OPEN_AI_KEY`: Klucz API OpenAI
- `AOAI_ENDPOINT`: URL punktu końcowego Azure OpenAI
- `AOAI_KEY`: Klucz API Azure OpenAI

### 2. connection_test.py
Skrypt do testowania połączenia z bazą danych MongoDB (Azure Cosmos DB).

Główne funkcje:
- `connect_to_cosmosdb(connection_string)`: Nawiązuje połączenie z bazą danych i zwraca obiekt klienta.

### 3. CRUD_operations.py
Implementacja podstawowych operacji CRUD dla bazy danych MongoDB.

Główne funkcje:
- `connect_to_cosmosdb(connection_string)`: Nawiązuje połączenie z bazą danych.
- `get_collection(client, db_name, collection_name)`: Pobiera określoną kolekcję z bazy danych.
- `insert_document(collection, document)`: Wstawia dokument do kolekcji.
- `read_documents(collection, query)`: Odczytuje dokumenty z kolekcji na podstawie zapytania.
- `update_document(collection, query, new_values)`: Aktualizuje dokument w kolekcji.
- `delete_document(collection, query)`: Usuwa dokument z kolekcji.
- `find_similar_documents(collection, embedding, threshold=0.9)`: Wyszukuje podobne dokumenty na podstawie embeddingu.

### 4. GUI_alternative.py
Alternatywna implementacja graficznego interfejsu użytkownika do zarządzania bazą danych MongoDB.

Główne funkcje:
- Połączenie z bazą danych
- Zarządzanie kolekcjami (tworzenie, przełączanie, usuwanie)
- Operacje CRUD na dokumentach
- Wyświetlanie logów operacji

### 5. GUI_CRUD.py
Implementacja graficznego interfejsu użytkownika do wykonywania operacji CRUD na bazie danych MongoDB.

Główne funkcje:
- Połączenie z bazą danych
- Tworzenie i usuwanie kolekcji
- Operacje CRUD na dokumentach
- Wczytywanie dokumentów z plików
- Wyświetlanie logów operacji

## Instrukcje użytkowania

1. Skopiuj plik `.env.example` do `.env` i uzupełnij odpowiednie wartości zmiennych środowiskowych.
2. Użyj `connection_test.py` do sprawdzenia poprawności połączenia z bazą danych.
3. Wykorzystaj `CRUD_operations.py` do wykonywania operacji na bazie danych z poziomu kodu.
4. Uruchom `GUI_alternative.py` lub `GUI_CRUD.py`, aby korzystać z graficznego interfejsu do zarządzania bazą danych.

## Uwagi

- Upewnij się, że masz zainstalowane wszystkie wymagane biblioteki (pymongo, numpy, dotenv).
- Przed użyciem w środowisku produkcyjnym, należy dokładnie przetestować kod i zabezpieczyć wrażliwe dane.
- Interfejsy graficzne (`GUI_alternative.py` i `GUI_CRUD.py`) oferują różne podejścia do zarządzania bazą danych - wybierz ten, który najlepiej odpowiada Twoim potrzebom.