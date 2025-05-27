const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const winston = require('winston');
const axios = require('axios');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: 'http://localhost:3000',
    methods: ['GET', 'POST'],
  },
});

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/backend.log' }),
  ],
});

app.use(express.json());

app.get('/health', (req, res) => {
  res.send('Backend is running');
});

app.post('/api/register', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:5000/register', req.body);
    logger.info('Face registration successful', { data: response.data });
    res.json(response.data);
  } catch (error) {
    logger.error('Error registering face', { error: error.message });
    res.status(500).json({ message: 'Error registering face' });
  }
});

app.post('/api/recognize', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:5001/recognize', req.body);
    logger.info('Face recognition completed', { data: response.data });
    res.json(response.data);
  } catch (error) {
    logger.error('Error recognizing face', { error: error.message });
    res.status(500).json({ message: 'Error recognizing face' });
  }
});

io.on('connection', (socket) => {
  logger.info('New client connected');
  socket.on('chat message', async (msg) => {
    try {
      const response = await axios.post('http://localhost:5002/rag', { query: msg });
      socket.emit('chat message', response.data.response);
    } catch (error) {
      logger.error('Error processing chat message', { error: error.message });
      socket.emit('chat message', 'Error processing query');
    }
  });
  socket.on('disconnect', () => {
    logger.info('Client disconnected');
  });
});

server.listen(3001, () => {
  logger.info('Backend server running on port 3001');
});