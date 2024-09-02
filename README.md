# WhatsApp Chatbot with RAG

This project implements a WhatsApp chatbot that uses Retrieval-Augmented Generation (RAG) to provide intelligent responses based on a knowledge base stored in a MongoDB database.

## Project Structure

```
WhatsApp-Chatbot/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── railway.json
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongodb_client.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   └── rag_engine.py
│   ├── whatsapp/
│   │   ├── __init__.py
│   │   └── whatsapp_client.py
│   └── api/
│       ├── __init__.py
│       └── webhook.py
│
└── tests/
    ├── __init__.py
    ├── test_mongodb_client.py
    ├── test_openai_client.py
    ├── test_rag_engine.py
    └── test_whatsapp_client.py
```

## Features

- WhatsApp integration for receiving and sending messages
- MongoDB (Cosmos DB) integration for storing and retrieving knowledge base
- OpenAI GPT-4 integration for generating responses
- Retrieval-Augmented Generation (RAG) for context-aware responses
- Webhook for handling incoming WhatsApp messages
- Containerized deployment using Railway

## Prerequisites

- Python 3.8+
- MongoDB account (or Cosmos DB with MongoDB API)
- OpenAI API key
- WhatsApp Business API access

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/WhatsApp-Chatbot.git
   cd WhatsApp-Chatbot
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Copy the `.env.example` file to `.env` and fill in your configuration details:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your specific configuration details:
   - MongoDB/Cosmos DB connection string
   - OpenAI API key
   - WhatsApp API credentials
   - Other configuration parameters

## Running the Application

To run the application locally:

```
python src/main.py
```

The application will start and listen on the port specified in your `.env` file (default is 8080).

## Deployment

This project is configured for deployment on Railway. To deploy:

1. Push your code to a GitHub repository.
2. Connect your Railway account to your GitHub repository.
3. Railway will automatically deploy your application using the configuration in `railway.json`.

## Testing

To run the tests:

```
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.