# Szczegółowy przegląd folderu: rag-like-capabilities

## Cel folderu
Folder "rag-like-capabilities" zawiera zbiór skryptów implementujących funkcjonalność RAG (Retrieval-Augmented Generation). Każdy skrypt prezentuje różne podejście do wyszukiwania informacji i generowania odpowiedzi, wykorzystując bazę danych MongoDB (Azure Cosmos DB) oraz API OpenAI.

## Analiza plików

### 1. fin_euvic.py

#### Główne funkcje
- Łączenie z bazą danych MongoDB
- Generowanie embeddings za pomocą API OpenAI
- Wyszukiwanie wektorowe w bazie danych
- Implementacja RAG z użyciem modelu GPT-4

#### Wyszukiwanie: ODBYWA SIĘ W BAZIE DANYCH

#### Kluczowe aspekty
- Wykorzystuje `$search` z MongoDB dla wyszukiwania wektorowego
- Implementuje RAG z użyciem modelu GPT-4
- Obsługuje zarówno wyszukiwanie wektorowe, jak i generowanie odpowiedzi

#### Snippety kodu
```python
def vector_search(collection, query, num_results=2):
    query_embedding = generate_embeddings(query)
    pipeline = [
        {
            '$search': {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "contentVector",
                    "k": num_results
                },
                "returnStoredSource": True
            }
        },
        {'$project': {'similarityScore': {'$meta': 'searchScore'}, 'document': '$$ROOT'}}
    ]
    results = collection.aggregate(pipeline)
    return results
```

#### Prompt systemu
```python
system_prompt = """
You are a helpful assistant designed to provide information about the Euvic Services presentation.
Try to answer questions based on the information provided in the presentation content below.
If you are asked a question that isn't covered in the presentation, respond based on the given information and your best judgment.

Presentation content:
"""
```

#### Instrukcja obsługi
1. Upewnij się, że masz skonfigurowane zmienne środowiskowe (CONNECTION_STRING, DB_NAME, COLLECTION_NAME, OPEN_AI_KEY).
2. Uruchom skrypt.
3. Skrypt automatycznie wykona przykładowe zapytania zdefiniowane w `queries`.
4. Dla każdego zapytania zobaczysz wyniki wyszukiwania wektorowego oraz odpowiedź wygenerowaną przez model RAG.

### 2. rag_like_corrected.py

#### Główne funkcje
- Wyszukiwanie wektorowe i semantyczne w bazie danych
- Generowanie odpowiedzi za pomocą OpenAI API
- Interaktywne menu dla różnych operacji

#### Wyszukiwanie: ODBYWA SIĘ W BAZIE DANYCH

#### Kluczowe aspekty
- Wykorzystuje `$search` z MongoDB dla obu typów wyszukiwania
- Oferuje menu interaktywne dla różnych operacji
- Implementuje generowanie odpowiedzi z użyciem GPT-4

#### Snippety kodu
```python
def vector_search(collection, query_vector, top_k=5):
    results = list(collection.aggregate([
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_vector,
                    "path": "vector",
                    "k": top_k
                }
            }
        },
        {
            "$project": {
                "content": 1,
                "score": {"$meta": "searchScore"}
            }
        }
    ]))
    return results
```

#### Instrukcja obsługi
1. Skonfiguruj zmienne środowiskowe w pliku .env.
2. Uruchom skrypt.
3. Wybierz opcję z menu:
   - 1: Wykonaj wyszukiwanie wektorowe
   - 2: Wykonaj wyszukiwanie semantyczne
   - 3: Uzyskaj odpowiedź OpenAI na podstawie wyników wyszukiwania
   - 4: Wyjście
4. Dla opcji 1-3, wprowadź zapytanie gdy zostaniesz o to poproszony.

### 3. rag_like_slow.py

#### Główne funkcje
- Wyszukiwanie wektorowe i semantyczne (lokalne)
- Generowanie odpowiedzi za pomocą OpenAI API
- Pomiar czasu wykonania operacji

#### Wyszukiwanie: NIE ODBYWA SIĘ W BAZIE DANYCH

#### Kluczowe aspekty
- Wczytuje wszystkie dokumenty do pamięci i wykonuje wyszukiwanie lokalnie
- Jest wolniejszy i mniej efektywny niż wersje wykorzystujące indeksy bazodanowe
- Implementuje podobne funkcjonalności jak rag_like_corrected.py, ale z inną metodą wyszukiwania

#### Snippety kodu
```python
def vector_search(collection, query_vector, top_k=5):
    documents = list(collection.find({}))
    similarities = cosine_similarity([query_vector], [doc['vector'] for doc in documents])[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    results = [{"content": documents[i]['content'], "score": float(similarities[i])} for i in top_indices]
    return results
```

#### Instrukcja obsługi
Identyczna jak dla rag_like_corrected.py, ale należy pamiętać, że operacje będą wolniejsze ze względu na lokalne przetwarzanie.

### 4. rag_on_json_testing.py

#### Główne funkcje
- Testowanie RAG na lokalnych plikach JSON
- Wyszukiwanie wektorowe i semantyczne (lokalne)
- Generowanie odpowiedzi za pomocą OpenAI API

#### Wyszukiwanie: NIE ODBYWA SIĘ W BAZIE DANYCH

#### Kluczowe aspekty
- Działa na lokalnych plikach JSON zamiast bazy danych
- Implementuje wyszukiwanie wektorowe i semantyczne w pamięci
- Służy głównie do testów i prototypowania

#### Snippety kodu
```python
def load_embeddings(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def semantic_search(collection, query_text, top_k=5):
    words = query_text.lower().split()
    results = []
    for doc in collection.find():
        content = doc['content'].lower()
        score = sum(word in content for word in words)
        if score > 0:
            results.append((doc, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
```

#### Instrukcja obsługi
1. Upewnij się, że masz plik JSON z embeddingami (ścieżka w zmiennej EMBEDDINGS_FILE).
2. Uruchom skrypt.
3. Wybierz opcję z menu:
   - 1: Załaduj embeddingi i wstaw dokumenty
   - 2: Wykonaj wyszukiwanie wektorowe
   - 3: Wykonaj wyszukiwanie semantyczne
   - 4: Uzyskaj odpowiedź OpenAI na podstawie wyników wyszukiwania
   - 5: Wyjście
4. Dla opcji 2-4, wprowadź zapytanie gdy zostaniesz o to poproszony.

### 5. viz_test.py

#### Główne funkcje
- Implementacja interfejsu webowego dla RAG z użyciem Flask
- Wyszukiwanie wektorowe w bazie danych
- Generowanie odpowiedzi za pomocą OpenAI API

#### Wyszukiwanie: ODBYWA SIĘ W BAZIE DANYCH

#### Kluczowe aspekty
- Łączy funkcjonalność RAG z interfejsem webowym
- Wykorzystuje `$search` z MongoDB dla wyszukiwania wektorowego
- Implementuje logowanie dla lepszego debugowania

#### Snippety kodu
```python
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form['question']
        num_results = int(request.form['num_results'])
        client_org = connect_to_cosmosdb(CONNECTION_STRING)
        if client_org is not None:
            db = client_org[DB_NAME]
            collection = db[COLLECTION_NAME]
            try:
                response = rag_with_vector_search(collection, question, num_results)
            except Exception as e:
                logging.error(f"Error processing query: {e}")
                response = "An error occurred during processing."
            finally:
                client_org.close()
        else:
            response = "Failed to connect to MongoDB."
        return jsonify({'response': response}), 200
    return render_template('index.html')
```

#### Prompt systemu
```python
system_prompt = """
You are a helpful assistant designed to provide information about the Euvic Services presentation.
Try to answer questions based on the information provided in the presentation content below.
If you are asked a question that isn't covered in the presentation, respond based on the given information and your best judgment.

Presentation content:
"""
```

#### Instrukcja obsługi
1. Upewnij się, że masz zainstalowane wszystkie wymagane biblioteki (Flask, OpenAI, pymongo, etc.).
2. Skonfiguruj zmienne środowiskowe w pliku .env.
3. Uruchom skrypt: `python viz_test.py`
4. Otwórz przeglądarkę i przejdź do `http://localhost:8080`
5. Wprowadź pytanie w formularzu i wybierz liczbę wyników do wyszukania.
6. Kliknij "Submit" aby otrzymać odpowiedź.

## Podsumowanie

Folder "rag-like-capabilities" zawiera różnorodne implementacje systemu RAG, prezentując różne podejścia do wyszukiwania i generowania odpowiedzi. Trzy skrypty (fin_euvic.py, rag_like_corrected.py, viz_test.py) wykorzystują wyszukiwanie bezpośrednio w bazie danych MongoDB, co jest bardziej efektywne dla dużych zbiorów danych. Dwa pozostałe skrypty (rag_like_slow.py, rag_on_json_testing.py) wykonują wyszukiwanie lokalnie, co może być użyteczne do testów i prototypowania na mniejszych zbiorach danych.

Wszystkie implementacje korzystają z API OpenAI do generowania embeddings i odpowiedzi, co stanowi kluczowy element podejścia RAG. Skrypty różnią się sposobem interakcji (od prostych skryptów konsolowych po interfejs webowy) oraz szczegółami implementacji wyszukiwania.

Przy wyborze odpowiedniego skryptu do użycia, należy wziąć pod uwagę:
1. Wielkość zbioru danych (dla dużych zbiorów zaleca się użycie wyszukiwania w bazie danych).
2. Potrzebę interfejsu użytkownika (viz_test.py oferuje interfejs webowy).
3. Cel użycia (testowanie vs. produkcja).
4. Wydajność (skrypty z wyszukiwaniem w bazie danych są bardziej wydajne).

Każdy skrypt wymaga odpowiedniej konfiguracji zmiennych środowiskowych, które powinny być ustawione w pliku .env. Kluczowe zmienne to CONNECTION_STRING (dla połączenia z MongoDB), OPEN_AI_KEY (dla API OpenAI) oraz nazwy bazy danych i kolekcji.

Podczas korzystania z tych skryptów należy pamiętać o bezpieczeństwie danych i odpowiednim zarządzaniu kluczami API. Skrypty te nie powinny być używane w środowisku produkcyjnym bez dodatkowych zabezpieczeń i optymalizacji.