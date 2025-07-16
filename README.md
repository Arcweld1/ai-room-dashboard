# AI Room Dashboard

A Flask-based web application for multi-AI chat interactions with support for OpenAI GPT and Google Gemini models. Features include real-time conversations, file uploads, conversation history, and Docker containerization.

## Features

- **Multi-AI Support**: Switch between OpenAI GPT-3.5 and Google Gemini
- **Real-time Chat**: Interactive chat interface with streaming responses
- **File Uploads**: Support for various file types (images, documents, text files)
- **Conversation History**: Persistent storage and viewing of chat sessions
- **Responsive Design**: Mobile-friendly interface
- **Docker Support**: Easy containerized deployment
- **Security**: Environment variable management for API keys

## Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (optional)
- Google Gemini API key (optional)
- Docker (for containerized deployment)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Arcweld1/ai-room-dashboard.git
   cd ai-room-dashboard
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

5. **Access the dashboard:**
   Open your browser and navigate to `http://localhost:5000`

### Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t ai-room-dashboard .
   ```

2. **Run with Docker:**
   ```bash
   docker run -p 5000:5000 --env-file .env ai-room-dashboard
   ```

2. **Or use Docker Compose (recommended):**
   ```bash
   docker-compose up -d
   ```

   To stop:
   ```bash
   docker-compose down
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | None |
| `GEMINI_API_KEY` | Google Gemini API key | None |
| `FLASK_SECRET_KEY` | Flask session secret key | `dev-secret-key` |
| `FLASK_ENV` | Flask environment | `development` |
| `MAX_CONTENT_LENGTH` | Maximum file upload size (bytes) | `16777216` (16MB) |
| `UPLOAD_FOLDER` | File upload directory | `uploads` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PORT` | Server port | `5000` |

### Supported File Types

- Text files: `.txt`
- Documents: `.pdf`, `.doc`, `.docx`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`

## API Endpoints

- `GET /` - Main chat interface
- `GET /history` - Conversation history
- `POST /chat` - Send chat message
- `POST /upload` - Upload file
- `POST /clear_conversation` - Clear current conversation
- `GET /health` - Health check endpoint

## Project Structure

```
ai-room-dashboard/
├── main.py                 # Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── templates/            # HTML templates
│   ├── room.html         # Chat interface
│   └── history.html      # Conversation history
├── static/               # Static assets
│   ├── style.css         # CSS styles
│   └── scripts.js        # JavaScript functionality
├── data/                 # Data storage
│   ├── app.log           # Application logs
│   └── history_*.json    # User conversation history
└── uploads/              # File uploads directory
```

## Usage

### Chat Interface

1. Select your preferred AI provider (OpenAI or Gemini)
2. Type your message in the input field
3. Press Enter or click Send
4. View AI responses in real-time
5. Upload files using the attachment button

### Conversation History

- Click the "History" tab to view past conversations
- Each session is timestamped and stored separately
- Click on messages to expand/collapse content

### File Uploads

- Click the attachment button (📎) to upload files
- Supported formats: images, documents, text files
- Files are stored in the uploads directory

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python main.py
```

### Logging

Application logs are written to:
- Console output
- `data/app.log` file

### Testing

Basic health check:
```bash
curl http://localhost:5000/health
```

## Security Notes

- Never commit actual API keys to version control
- Use strong, unique values for `FLASK_SECRET_KEY`
- Consider implementing rate limiting for production use
- File uploads are restricted to specific file types
- All uploads are stored locally (consider cloud storage for production)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are valid and properly set in `.env`
2. **File Upload Errors**: Check file size limits and supported formats
3. **Connection Issues**: Verify network connectivity and API endpoint availability
4. **Docker Issues**: Ensure Docker is installed and running

### Getting Help

- Check the application logs in `data/app.log`
- Verify environment variables are set correctly
- Ensure all dependencies are installed
- Check the health endpoint: `http://localhost:5000/health`

## Roadmap

- [ ] Real-time streaming responses
- [ ] Multiple conversation rooms
- [ ] User authentication
- [ ] Cloud storage integration
- [ ] Advanced file processing
- [ ] Rate limiting and quotas
- [ ] WebSocket support
- [ ] Plugin system for additional AI providers