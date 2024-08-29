# Azure-db-test2 Project Documentation

## Project Structure

```
Azure-db-test2/
├── connection-upload/
│   ├── .env
│   ├── .env.example
│   ├── connection_test.py
│   ├── CRUD_operations.py
│   ├── GUI_alternative.py
│   └── GUI_CRUD.py
├── json_embeddings/
│   ├── .env
│   ├── .env.example
│   ├── embeddings_ada_002.py
│   └── output_test.json
├── json_embeddings_azure/
│   ├── .env
│   ├── .env.example
│   ├── implementation_full_euvic.py
│   ├── output_test.json
│   └── test.json
├── multi_parser/
│   ├── .env
│   ├── .env.example
│   ├── automated_parsed_typed.py
│   ├── automated_parser.py
│   ├── automated_parser_viz.py
│   ├── Euvic_test_prez.pdf
│   ├── output_v1.json
│   ├── parser_org.py
│   └── test1.pdf
├── queries/
├── .env
│   ├── .env.example
│   ├── output_with_embeddings.json
│   └── semantic_vector_search.py
├── rag-like-capabilities/
│   └── templates/
│       └── index.html
├── whatsupp/
│   └── demo.py
│   ├── .env
│   └── .env.example
├── .env
├── .env.example
├── fin_euvic.py
├── rag_like_corrected.py
├── rag_like_slow.py
├── rag_on_json_testing.py
├── viz_test.py
├── LICENSE
└── README.md
```

## Folder Descriptions

### connection-upload/
Ten folder zawiera pliki związane z połączeniem do bazy danych i operacjami CRUD.

- `connection_test.py`: Skrypt do testowania połączenia z bazą danych.
- `CRUD_operations.py`: Implementacja podstawowych operacji CRUD.
- `GUI_alternative.py` i `GUI_CRUD.py`: Alternatywne implementacje GUI dla operacji CRUD.

### json_embeddings/
Folder ten zawiera pliki związane z generowaniem embeddings dla danych JSON.

- `embeddings_ada_002.py`: Skrypt do generowania embeddings przy użyciu modelu Ada-002.
- `output_test.json`: Plik wyjściowy z wynikami embeddings.

### json_embeddings_azure/
Ten folder zawiera implementację embeddings specyficzną dla Azure.

- `implementation_full_euvic.py`: Pełna implementacja embeddings dla Euvic na Azure.
- `output_test.json` i `test.json`: Pliki testowe i wyjściowe.

### multi_parser/
Folder zawierający różne parsery i skrypty do przetwarzania danych.

- `automated_parsed_typed.py`, `automated_parser.py`, `automated_parser_viz.py`: Różne wersje zautomatyzowanych parserów.
- `parser_org.py`: Oryginalny parser.
- `Euvic_test_prez.pdf` i `test1.pdf`: Pliki PDF do testowania parserów.

### queries/
Ten folder zawiera pliki związane z zapytaniami do bazy danych i wyszukiwaniem wektorowym.

- `semantic_vector_search.py`: Implementacja semantycznego wyszukiwania wektorowego.
- `output_with_embeddings.json`: Plik wyjściowy z wynikami wyszukiwania.

### rag-like-capabilities/
Folder zawierający implementację funkcjonalności podobnych do RAG (Retrieval-Augmented Generation).

- `templates/index.html`: Szablon HTML dla interfejsu użytkownika.

### Pliki w głównym katalogu
- `fin_euvic.py`: Główny skrypt dla funkcjonalności Euvic.
- `rag_like_corrected.py`, `rag_like_slow.py`, `rag_on_json_testing.py`: Różne implementacje i testy RAG.
- `viz_test.py`: Skrypt do testowania wizualizacji.
- `LICENSE`: Plik licencji projektu.
- `README.md`: Główny plik README projektu (ten dokument).

## Instrukcje użytkowania

1. Sklonuj repozytorium na swój lokalny komputer.
2. Zainstaluj wymagane zależności (lista zależności powinna być dodana do pliku `requirements.txt`).
3. Skonfiguruj pliki `.env` w każdym folderze na podstawie odpowiednich plików `.env.example`.
4. Uruchom skrypty w zależności od potrzeb:
   - Użyj skryptów z folderu `connection-upload/` do testowania połączenia i wykonywania operacji CRUD.
   - Generuj embeddings przy użyciu skryptów z folderów `json_embeddings/` lub `json_embeddings_azure/` -> uwaga tu narazie nie udało mi się zmusić Azure Open AI do współpracy.
   - Przetwarzaj dane przy użyciu parserów z folderu `multi_parser/`.
   - Wykonuj zapytania semantyczne przy użyciu skryptów z folderu `queries/`.
   - Testuj funkcjonalności RAG przy użyciu skryptów z folderu `rag-like-capabilities/` i głównego katalogu.

5. W razie potrzeby, dostosuj skrypty do swoich specyficznych wymagań.

## Uwagi

- Upewnij się, że masz odpowiednie uprawnienia i klucze dostępu do usług Azure, jeśli są wymagane.
- Regularnie aktualizuj pliki `.env.example`, aby odzwierciedlały wszystkie wymagane zmienne środowiskowe.
- Przed uruchomieniem skryptów na produkcji, przetestuj je dokładnie w środowisku deweloperskim.

## Kontakt

W przypadku pytań lub problemów, proszę o kontakt z administratorem projektu.
