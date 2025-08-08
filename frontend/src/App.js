import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000/api/';

function App() {
  const [messages, setMessages] = useState([]);
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
      const response = await axios.post(`${API_URL}chat/`, { message: input });
      const { message, request_id } = response.data;
      const botMessage = { sender: 'bot', text: `${message} (ID: ${request_id})` };
      setMessages(prev => [...prev, botMessage]);
      pollStatus(request_id);
    } catch (error) {
      const errorMessage = { sender: 'bot', text: 'Sorry, I could not process your request.' };
      setMessages(prev => [...prev, errorMessage]);
      setIsProcessing(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>VMware Provisioner Bot</h1>
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
          placeholder="e.g., create a medium ubuntu server"
          disabled={isProcessing}
        />
        <button type="submit" disabled={isProcessing}>Send</button>
      </form>
    </div>
  );
}

export default App;

