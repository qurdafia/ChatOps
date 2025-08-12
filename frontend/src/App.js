import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000/api/';

function App() {

  // Initial message
  const initialMessage = {
    sender: 'bot',
    text: "Hello! I'm your self-service VM Provisioner Bot. 🤖\n\n" +
          "You can ask me to 'create', 'provision', or 'build' a server.\n\n" +
          "Available Sizes: Small, Medium, Large\n" +
          "Available OS: RHEL"
  };

  const [messages, setMessages] = useState([initialMessage]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // frontend/src/App.js

// ... (inside the App component) ...

const pollStatus = (requestId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}status/${requestId}/`);
        const { status, output, vm_details } = response.data; // Destructure new data

        if (status === 'SUCCESS' || status === 'FAILED') {
          clearInterval(interval);
          let finalMessage = `Request ${requestId} ${status.toLowerCase()}.`;

          // --- NEW: Format the success message ---
          if (status === 'SUCCESS' && vm_details) {
            finalMessage = `✅ VM '${vm_details.name}' created successfully!\n\n` +
                         `   • CPU: ${vm_details.cpu} vCPUs\n` +
                         `   • RAM: ${vm_details.memory} GB\n` +
                         `   • IP Address: ${vm_details.ip_address}`;
          } else if (status === 'FAILED') {
            // For failed messages, show the log output
            finalMessage = `❌ Request ${requestId} failed.\n\nError:\n${output}`;
          }
          // ------------------------------------

          setMessages(prev => [...prev, { sender: 'bot', text: finalMessage }]);
          setIsProcessing(false);
        }
      } catch (error) {
        clearInterval(interval);
        console.error("Polling error:", error);
        setIsProcessing(false);
      }
    }, 5000);
  };

// ... (rest of the component) ...

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);
    setInput('');

    try {
      // This is the POST request to your Django view
      const response = await axios.post(`${API_URL}chat/`, { message: input });
      const { message, request_id } = response.data;
      const botMessage = { sender: 'bot', text: `${message} (ID: ${request_id})` };
      setMessages(prev => [...prev, botMessage]);
      pollStatus(request_id);
    } catch (error) {
      // --- THE FIX IS HERE ---
      // Check if the server sent a specific error message, otherwise use a generic one.
      const errorText = error.response?.data?.error || 'Sorry, an unexpected error occurred.';
      const errorMessage = { sender: 'bot', text: `⚠️ ${errorText}` };
      // -----------------------
      
      setMessages(prev => [...prev, errorMessage]);
      setIsProcessing(false); // Make sure to stop processing on error
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🤖 Server Provisioning Assistant</h1>
      </header>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <pre>{msg.text}</pre>
          </div>
        ))}
        {isProcessing && <div className="message bot typing"><span></span><span></span><span></span></div>}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g., create a medium rhel server"
          disabled={isProcessing}
        />
        <button type="submit" disabled={isProcessing}>Send</button>
      </form>
    </div>
  );
}

export default App;

