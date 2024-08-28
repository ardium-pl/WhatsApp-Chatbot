# Przegląd folderu: multi_parser

## Cel folderu
Folder multi_parser zawiera skrypty i pliki związane z parsowaniem różnych typów dokumentów i konwersją ich do formatu JSON. Głównym celem jest zapewnienie uniwersalnego narzędzia do przetwarzania różnorodnych formatów plików.

## Kluczowe pliki i ich funkcje

1. **automated_parser_viz.py**
   - Główny skrypt z interfejsem graficznym do parsowania plików.
   - Kluczowe funkcje:
     ```python
     def parse_file(file_path):
         # Wybiera odpowiednią funkcję parsującą na podstawie rozszerzenia pliku
     
     class FileParserApp(tk.Tk):
         # Implementacja interfejsu graficznego do parsowania plików
     ```
   - Obsługuje formaty: PPTX, DOC/DOCX, PDF, XML, XLSX/XLS, CSV, TXT, RTF.

2. **automated_parsed_typed.py**
   - Wersja skryptu z dodanymi adnotacjami typów.
   - Podobna funkcjonalność do automated_parser_viz.py, ale bez GUI.

3. **automated_parser.py**
   - Podstawowa wersja skryptu do parsowania plików.
   - Zawiera funkcje parsujące dla różnych formatów plików.

4. **output_v1.json**
   - Przykładowy plik wyjściowy zawierający sparsowane dane.

5. **.env.example**
   - Przykładowy plik konfiguracyjny z zmiennymi środowiskowymi.

## Kluczowe aspekty implementacji

1. Uniwersalne parsowanie:
   ```python
   parsers = {
       '.pptx': parse_pptx,
       '.doc': parse_doc,
       '.docx': parse_doc,
       '.pdf': parse_pdf,
       # ... inne formaty
   }
   ```

2. Struktura wyjściowa JSON:
   - Różna dla każdego typu pliku, np. dla PDF:
     ```python
     {"pages": [{"Page 1": "treść strony 1"}, {"Page 2": "treść strony 2"}]}
     ```

3. Obsługa kodowania:
   ```python
   def detect_encoding(file_path):
       with open(file_path, 'rb') as file:
           raw = file.read()
       return chardet.detect(raw)['encoding']
   ```

4. Interfejs graficzny (w automated_parser_viz.py):
   - Wykorzystuje tkinter do stworzenia prostego GUI.
   - Zawiera pasek postępu i okno logowania.

## Proces przetwarzania
1. Wybór folderu wejściowego i wyjściowego.
2. Iteracja przez pliki w folderze wejściowym.
3. Parsowanie każdego pliku na podstawie jego rozszerzenia.
4. Zapisywanie wyników w formacie JSON w folderze wyjściowym.

## Potencjalne zastosowania
- Masowe przetwarzanie dokumentów różnych typów.
- Przygotowanie danych do dalszej analizy lub indeksowania.
- Migracja danych między różnymi systemami.

## Uwagi
- Skrypty wymagają zainstalowania różnych bibliotek do obsługi formatów plików (np. python-pptx, PyPDF2).
- Obecna implementacja może być rozszerzona o obsługę dodatkowych formatów plików.
- Warto rozważyć dodanie obsługi błędów i testów jednostkowych dla zwiększenia niezawodności.


## Proces przetwarzania i praktyczne użycie

### Struktura folderów
Skrypty zakładają następującą strukturę folderów:

```
C:\Users\szyme\to_be_parsed\
├── input\
│   ├── (pliki do przetworzenia)
└── output\
    ├── pdf\
    ├── docx\
    ├── xlsx\
    └── (inne foldery dla każdego typu pliku)
```
## *Folder `to_be_parsed` zawiera podfoldery `input` i `output`.* -> *Folder `output` zawiera podfoldery dla każdego typu pliku wygenerowane na podstawie typów plików w input. Jedynce co tu muszą być te dwa foldery: `input` `output`*
### Krok po kroku instrukcja użycia

1. **Przygotowanie środowiska**:
   - Upewnij się, że masz zainstalowane wszystkie wymagane biblioteki Python.
   - Skopiuj plik `.env.example` do `.env` i uzupełnij wymagane zmienne środowiskowe.

2. **Przygotowanie folderów**:
   - Utwórz główny folder `to_be_parsed` (lub zmień ścieżkę w kodzie).
   - W głównym folderze utwórz podfoldery `input` i `output`.

3. **Umieszczenie plików do przetworzenia**:
   - Skopiuj wszystkie pliki, które chcesz przetworzyć, do folderu `input`.

4. **Uruchomienie skryptu**:
   - Dla wersji z GUI: Uruchom `automated_parser_viz.py`.
   - Dla wersji bez GUI: Uruchom `automated_parser.py` lub `automated_parsed_typed.py`.

5. **Proces przetwarzania**:
   - Skrypt automatycznie utworzy podfoldery w `output` dla każdego typu pliku.
   - Każdy plik zostanie przetworzony i zapisany jako JSON w odpowiednim podfolderze.

6. **Wyniki**:
   - Sparsowane pliki JSON znajdziesz w folderze `output`, w podfolderach odpowiadających typom plików.

### Szczegóły implementacji

```python
def process_folder(input_folder, output_folder):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            input_file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()
            extension_folder = os.path.join(output_folder, file_extension.lstrip('.'))
            output_file_path = os.path.join(extension_folder, os.path.splitext(file)[0] + '.json')

            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            try:
                parsed_content = parse_file(input_file_path)
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(parsed_content, f, ensure_ascii=False, indent=2)
                print(f"Processed: {input_file_path} -> {output_file_path}")
            except Exception as e:
                print(f"Error processing {input_file_path}: {str(e)}")
```

### Obsługiwane typy plików
- PPTX: Prezentacje PowerPoint
- DOC/DOCX: Dokumenty Word
- PDF: Dokumenty PDF
- XML: Pliki XML
- XLSX/XLS: Arkusze Excel
- CSV: Pliki CSV
- TXT: Pliki tekstowe
- RTF: Dokumenty w formacie Rich Text Format

### Uwagi dotyczące użytkowania
- Upewnij się, że masz odpowiednie uprawnienia do odczytu plików wejściowych i zapisu w folderze wyjściowym.
- Dla dużych plików lub dużej liczby plików, proces może zająć dłuższy czas.
- W przypadku błędów podczas przetwarzania, sprawdź logi wyświetlane w konsoli lub w oknie GUI.
- Rozważ regularne tworzenie kopii zapasowych oryginalnych plików przed przetwarzaniem.

### Rozwiązywanie problemów
- Jeśli skrypt nie może otworzyć pliku, sprawdź, czy nie jest on otwarty w innym programie.
- W przypadku błędów związanych z kodowaniem, możesz spróbować ręcznie określić kodowanie w funkcji `detect_encoding`.
- Jeśli wyniki parsowania są niepełne lub niepoprawne, może być konieczne dostosowanie funkcji parsujących dla konkretnych typów plików.