# Przegląd folderu: queries

## UWAGA: TESTY LOKALNE, NIE BAZA DANYCH

**Ten folder służy wyłącznie do testowania funkcjonalności na lokalnych plikach, a nie w bazie danych. Wszystkie operacje są wykonywane na plikach lokalnych, co pozwala na szybkie prototypowanie i testowanie bez konieczności połączenia z bazą danych.**

## Cel folderu
Folder "queries" zawiera skrypty i pliki konfiguracyjne służące do testowania funkcjonalności wyszukiwania semantycznego i wektorowego na lokalnych plikach JSON. Głównym celem jest umożliwienie szybkiego prototypowania i testowania algorytmów wyszukiwania bez konieczności interakcji z rzeczywistą bazą danych.

## Kluczowe pliki i ich funkcje

1. **semantic_vector_search.py**
   - Główny skrypt do testowania wyszukiwania semantycznego i wektorowego.
   - Kluczowe funkcje:
     ```python
     def load_embeddings(file_path):
         # Wczytuje embeddingi z lokalnego pliku JSON
     
     def vector_search(collection, query_vector, top_k=5):
         # Wykonuje wyszukiwanie wektorowe na lokalnej kolekcji dokumentów
     
     def semantic_search(collection, query_text, top_k=5):
         # Wykonuje wyszukiwanie semantyczne na lokalnej kolekcji dokumentów
     ```
   - Symuluje operacje bazodanowe na lokalnych strukturach danych.

2. **.env**
   - Plik konfiguracyjny z rzeczywistymi zmiennymi środowiskowymi.
   - **WAŻNE: Ten plik zawiera wrażliwe dane i nie powinien być udostępniany ani przechowywany w repozytorium.**

3. **.env.example**
   - Przykładowy plik konfiguracyjny pokazujący strukturę wymaganych zmiennych środowiskowych.
   - Nie zawiera rzeczywistych danych, służy jako szablon.

## Kluczowe aspekty implementacji

1. Symulacja operacji bazodanowych:
   ```python
   def get_or_create_collection(client, db_name, collection_name):
       # Ta funkcja symuluje tworzenie kolekcji, ale operuje na lokalnych strukturach
   ```

2. Wczytywanie danych z pliku lokalnego:
   ```python
   embeddings_data = load_embeddings(EMBEDDINGS_FILE)
   ```

3. Wyszukiwanie wektorowe i semantyczne:
   ```python
   results = vector_search(collection, query_vector)
   results = semantic_search(collection, query_text)
   ```

## Proces testowania
1. Wczytanie embeddings z lokalnego pliku JSON.
2. Symulacja insertu dokumentów do "kolekcji" (w rzeczywistości lokalnej struktury danych).
3. Wykonanie wyszukiwania wektorowego lub semantycznego na lokalnych danych.
4. Wyświetlenie wyników wyszukiwania.

## Uwagi dotyczące użytkowania
- **Wszystkie operacje są wykonywane lokalnie, bez rzeczywistego połączenia z bazą danych.**
- Skrypt używa zmiennych środowiskowych do konfiguracji, ale w rzeczywistości operuje na lokalnych plikach.
- Embeddingi są wczytywane z pliku określonego w zmiennej `EMBEDDINGS_FILE`.
- Wyniki wyszukiwania są wyświetlane w konsoli, bez zapisywania ich do bazy danych.

## Potencjalne zastosowania
- Szybkie prototypowanie algorytmów wyszukiwania.
- Testowanie różnych podejść do wyszukiwania semantycznego i wektorowego bez obciążania bazy danych.
- Debugowanie i optymalizacja funkcji wyszukiwania przed integracją z rzeczywistą bazą danych.

## Ważne przypomnienie
**Ten folder i zawarte w nim skrypty są przeznaczone wyłącznie do celów testowych i rozwojowych. Nie należy używać ich do przetwarzania rzeczywistych danych produkcyjnych lub w środowisku produkcyjnym. Wszystkie operacje są symulowane na plikach lokalnych.**