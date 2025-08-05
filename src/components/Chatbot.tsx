import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatbotProps {
  isVisible: boolean;
  onClose: () => void;
}

const Chatbot: React.FC<ChatbotProps> = ({ isVisible, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! Welcome to Electro. How can I help you today?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isVisible) {
      document.body.classList.add('chatbot-open');
    } else {
      document.body.classList.remove('chatbot-open');
    }

    return () => {
      document.body.classList.remove('chatbot-open');
    };
  }, [isVisible]);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate bot response
    setTimeout(() => {
      const botResponse: Message = {
        id: Date.now() + 1,
        text: getBotResponse(inputValue),
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  const getBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('help') || input.includes('support')) {
      return "I'm here to help! You can ask me about our products, shipping, returns, or any other questions you have.";
    } else if (input.includes('product') || input.includes('laptop') || input.includes('phone')) {
      return "We have a great selection of electronics! Check out our Products page for laptops, smartphones, tablets, and more. Is there a specific product you're looking for?";
    } else if (input.includes('shipping') || input.includes('delivery')) {
      return "We offer free shipping on orders over $50! Standard delivery takes 3-5 business days, and express shipping is available for faster delivery.";
    } else if (input.includes('return') || input.includes('refund')) {
      return "We have a 30-day return policy. If you're not satisfied with your purchase, you can return it within 30 days for a full refund.";
    } else if (input.includes('price') || input.includes('cost') || input.includes('discount')) {
      return "We regularly offer special deals and discounts! Check our homepage for current promotions, or sign up for our newsletter to get exclusive offers.";
    } else if (input.includes('cart') || input.includes('checkout')) {
      return "Having trouble with your cart? Make sure you're logged in to save your items. If you need help with checkout, I can guide you through the process!";
    } else if (input.includes('account') || input.includes('login') || input.includes('register')) {
      return "You can create an account or login using the account icon in the top right. Having an account allows you to save your cart, track orders, and access exclusive deals!";
    } else if (input.includes('hi') || input.includes('hello') || input.includes('hey')) {
      return "Hello there! Thanks for visiting Electro. What can I help you find today?";
    } else if (input.includes('bye') || input.includes('goodbye') || input.includes('thanks')) {
      return "You're welcome! Feel free to reach out if you need any more help. Happy shopping at Electro! 😊";
    } else {
      const responses = [
        "That's a great question! Let me help you with that. Could you provide more details?",
        "I'd be happy to assist you with that! Can you tell me more about what you're looking for?",
        "Thanks for your question! For more specific information, you can also contact our customer service team.",
        "I understand your concern. Is there anything specific about our products or services I can help clarify?",
        "Great question! Feel free to browse our products or let me know if you need recommendations for any specific electronics."
      ];
      return responses[Math.floor(Math.random() * responses.length)];
    }
  };

  if (!isVisible) return null;

  return (
    <div className="chatbot-overlay">
      <div className="chatbot-container">
        <div className="chatbot-header">
          <div className="chatbot-header-info">
            <div className="chatbot-avatar">🤖</div>
            <div className="chatbot-header-text">
              <h4>Electro Assistant</h4>
              <span className="chatbot-status">Online</span>
            </div>
          </div>
          <button className="chatbot-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="chatbot-messages">
          {messages.map((message) => (
            <div key={message.id} className={`chatbot-message ${message.isUser ? 'user' : 'bot'}`}>
              <div className="chatbot-message-content">
                {message.text}
              </div>
              <div className="chatbot-message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="chatbot-message bot">
              <div className="chatbot-message-content">
                <div className="chatbot-typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chatbot-input-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="chatbot-input"
            maxLength={500}
          />
          <button type="submit" className="chatbot-send-btn" disabled={!inputValue.trim()}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill="currentColor"/>
            </svg>
          </button>
        </form>

        <div className="chatbot-footer">
          <span>Powered by Electro AI</span>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
