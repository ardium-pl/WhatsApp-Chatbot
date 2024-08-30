# WhatsApp Chatbot with RAG

This project implements a WhatsApp chatbot using Flask, integrated with OpenAI's GPT model and MongoDB for Retrieval-Augmented Generation (RAG). The bot can answer questions based on information stored in a MongoDB database.

## Features

- WhatsApp message handling
- Integration with OpenAI's GPT model for natural language processing
- MongoDB integration for storing and retrieving context
- Vector search for relevant information retrieval
- Webhook verification for WhatsApp API
- Retrieval-Augmented Generation (RAG) for context-aware responses
- Error handling and logging

## Prerequisites

- Python 3.7+
- Flask
- PyMongo
- OpenAI Python Client
- Requests
- python-dotenv
- A WhatsApp Business Account
- An OpenAI API key
- A MongoDB database (Azure Cosmos DB with MongoDB API)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/whatsapp-chatbot.git
   cd whatsapp-chatbot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables (see Environment Variables section below).

## Configuration

Create a `.env` file in the root directory and add the following environment variables:

```
# See .env.example for a complete list of required variables
```

## Usage

1. Start the Flask server:
   ```
   python demo.py
   ```

2. Set up your WhatsApp Business API to forward messages to your webhook URL.

3. The bot will now respond to incoming WhatsApp messages using the RAG system.

## Project Structure

```
whatsapp-chatbot/
│
├── whatsapp/
│   ├── __init__.py
│   ├── demo.py              # Main application file
│   ├── .env                 # Environment variables (not in version control)
│   ├── .env.example         # Example environment variables
│   └── railway.json         # Railway deployment configuration
│
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── railway.json             # Railway deployment configuration
```

## Detailed Component Descriptions

### demo.py

This is the main application file containing:
- Flask application setup
- MongoDB connection and operations
- OpenAI API integration
- WhatsApp message handling logic
- RAG implementation
- Webhook routes for incoming messages and verification

### railway.json

Configuration file for deployment on Railway platform, specifying:
- Build settings
- Start command
- Restart policy

### requirements.txt

Lists all Python packages required for the project, including:
- Flask
- gunicorn
- python-dotenv
- requests
- pymongo
- openai
- tenacity

## Environment Variables

Key environment variables include:
- `COSMOSDB_CONNECTION_STRING`: MongoDB connection string
- `DB_NAME`: Database name
- `COSMOS_COLLECTION_NAME`: Collection name for storing data
- `OPEN_AI_KEY`: OpenAI API key
- `ACCESS_TOKEN`: WhatsApp API access token
- `PHONE_NUMBER_ID`: WhatsApp phone number ID
- `WEBHOOK_VERIFY_TOKEN`: Token for webhook verification

## RAG (Retrieval-Augmented Generation) Process

1. Incoming message is received via WhatsApp API
2. Vector search is performed on the MongoDB database to find relevant context
3. Retrieved context is combined with the user's query
4. Combined input is sent to OpenAI's GPT model
5. Generated response is sent back to the user via WhatsApp

## Error Handling and Logging

The application includes comprehensive error handling and logging to facilitate debugging and monitoring. Key areas include:
- MongoDB connection errors
- WhatsApp API communication errors
- OpenAI API errors
- General request processing errors

## Deployment

This project is configured for deployment on Railway. The `railway.json` file specifies the build and deployment settings. To deploy:

1. Set up a Railway account
2. Connect your GitHub repository to Railway
3. Configure environment variables in Railway dashboard
4. Deploy the application

## Security Considerations

- Keep your `.env` file secure and never commit it to version control
- Regularly rotate your API keys and access tokens
- Ensure your MongoDB instance is properly secured
- Use HTTPS for all API communications

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Support

If you encounter any problems or have any questions, please open an issue in the GitHub repository.