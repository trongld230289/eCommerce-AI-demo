import React, { useState, useRef, useEffect } from 'react';
import { transcribeAudio, transcribeAudioWithTranslation } from '../../services/whisperService';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone, faMicrophoneSlash } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../../contexts/AuthContext';
import { chatbotService } from '../../services/chatbotService';
import { Product } from '../../contexts/ShopContext';
import './Chatbot.css';

// Add type declarations for Web Speech API
interface Window {
  SpeechRecognition: any;
  webkitSpeechRecognition: any;
}

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  products?: Product[];
}

interface ChatbotProps {
  isVisible: boolean;
  onClose: () => void;
}

const Chatbot: React.FC<ChatbotProps> = ({ isVisible, onClose }) => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
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
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [lastSearchResults, setLastSearchResults] = useState<Product[]>([]);
  const [lastSearchQuery, setLastSearchQuery] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Hybrid: Use Web Speech API for voice activity detection, MediaRecorder for audio capture
  useEffect(() => {
    let recorder: MediaRecorder | null = null;
    let speechRecognition: any = null;
    let stream: MediaStream | null = null;
    let chunks: Blob[] = [];

    const startRecording = async () => {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Use the best supported format for MediaRecorder
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        mimeType = 'audio/webm';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      }
      
      recorder = new MediaRecorder(stream, { mimeType });
      setMediaRecorder(recorder);
      chunks = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };
      recorder.onstop = async () => {
        setIsListening(false);
        const audioBlob = new Blob(chunks, { type: mimeType });
        setAudioChunks([]);
        try {
          setInputValue('...transcribing');
          const result = await transcribeAudioWithTranslation(audioBlob);
          
          // Show the original Vietnamese text to user
          setInputValue(result.displayText);
          
          // Send the English text to chatbot for processing
          if (result.chatbotText && result.chatbotText.trim()) {
            sendMessage(result.chatbotText);
          }
        } catch (err) {
          setInputValue('');
          alert('Transcription failed');
        }
        chunks = [];
      };
      recorder.start();
      setIsListening(true);
    };

    const stopRecording = async () => {
      if (recorder && recorder.state !== 'inactive') {
        recorder.stop();
      }
      setIsListening(false);
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };

    // Setup SpeechRecognition for voice activity detection
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      speechRecognition = new SpeechRecognition();
      speechRecognition.continuous = false;
      speechRecognition.interimResults = false;
      speechRecognition.lang = 'vi-VN'; // Vietnamese

      speechRecognition.onstart = () => {
        startRecording();
      };
      speechRecognition.onend = async () => {
        await stopRecording();
      };
      speechRecognition.onerror = async () => {
        await stopRecording();
      };
      setRecognition(speechRecognition);
    }
    // eslint-disable-next-line
  }, []);

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

  // sendMessage can accept a string (for voice) or event (for form)
  const sendMessage = async (eOrMessage: React.FormEvent | string) => {
    let messageText = '';
    if (typeof eOrMessage === 'string') {
      messageText = eOrMessage;
    } else {
      eOrMessage.preventDefault();
      messageText = inputValue;
    }
    if (!messageText.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      text: messageText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Check if user is asking to see all results from previous search
      const isShowAllRequest = (inputValue.toLowerCase().includes('show all') || 
                               inputValue.toLowerCase().includes('see all') ||
                               inputValue.toLowerCase().includes('view all') ||
                               (inputValue.toLowerCase().includes('yes') && lastSearchResults.length > 0));
      
      if (isShowAllRequest && lastSearchResults.length > 0) {
        // Create search URL with the last query
        const searchParams = new URLSearchParams();
        searchParams.append('q', lastSearchQuery);
        searchParams.append('chatbot', 'true');
        
        const showAllMessage: Message = {
          id: Date.now() + 1,
          text: `Perfect! I'll show you all ${lastSearchResults.length} results on the products page.`,
          isUser: false,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, showAllMessage]);
        
        setTimeout(() => {
          navigate(`/products?${searchParams.toString()}`);
        }, 1500);
        
        return;
      }

      // Call the backend chatbot API
      const response = await chatbotService.sendMessage({
        message: messageText,
        user_id: currentUser?.uid
      });

      console.log('Chatbot response received:', response);
      console.log('Products in response:', response.products);
      console.log('Smart search used:', response.smart_search_used);

      // Handle smart search responses differently
      if (response.smart_search_used && response.products && response.products.length > 0) {
        // Store search results for potential "show all" request
        setLastSearchResults(response.products);
        setLastSearchQuery(messageText);
        
        // Smart search found products - show them in chatbot first
        const smartSearchMessage: Message = {
          id: Date.now() + 1,
          text: response.response + `\n\nFilters detected: ${JSON.stringify(response.parsed_filters || {})}`,
          isUser: false,
          timestamp: new Date(),
          products: response.products.slice(0, 3) // Show top 3 products in chat
        };
        
        setMessages(prev => [...prev, smartSearchMessage]);

        // If there are many results, offer to show all
        if (response.products.length > 3) {
          setTimeout(() => {
            const moreResultsMessage: Message = {
              id: Date.now() + 2,
              text: `I found ${response.products?.length} total results. Would you like me to show you all of them on the products page?`,
              isUser: false,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, moreResultsMessage]);
          }, 1000);
        }
      }
      // Check if we should redirect to search page (traditional behavior)
      else if (response.redirect_url && response.redirect_url !== '') {
        // Add a message about redirecting
        const redirectMessage: Message = {
          id: Date.now() + 1,
          text: `${response.response}\n\nRedirecting you to the search page to show all results...`,
          isUser: false,
          timestamp: new Date(),
          products: response.products?.slice(0, 2) // Show just a preview
        };
        
        setMessages(prev => [...prev, redirectMessage]);
        
        // Close chatbot and redirect after a short delay
        setTimeout(() => {
          // onClose();
          navigate(response.redirect_url!);
        }, 2000);
      } else {
        // Normal chatbot response
        const botResponse: Message = {
          id: Date.now() + 1,
          text: response.response,
          isUser: false,
          timestamp: new Date(),
          products: response.products
        };

        setMessages(prev => [...prev, botResponse]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Fallback to local response
      const botResponse: Message = {
        id: Date.now() + 1,
        text: getBotResponse(messageText),
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  // Start/stop voice chat naturally
  const toggleVoiceRecording = async () => {
    if (!recognition) {
      alert('Speech recognition not supported in your browser.');
      return;
    }
    if (isListening) {
      recognition.stop();
    } else {
      setAudioChunks([]);
      recognition.start();
    }
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
              
              {/* Render products if available */}
              {message.products && message.products.length > 0 && (
                <div className="chatbot-products">
                  <div className="chatbot-products-grid">
                    {message.products.slice(0, 3).map((product) => (
                      <div key={product.id} className="chatbot-product-item">
                        <div className="chatbot-product-card">
                          <img src={product.imageUrl} alt={product.name} className="chatbot-product-image" />
                          <div className="chatbot-product-info">
                            <h4 className="chatbot-product-name">{product.name}</h4>
                            <p className="chatbot-product-brand">{product.brand}</p>
                            <p className="chatbot-product-price">
                              ${product.price}
                              {product.original_price && (
                                <span className="chatbot-product-original-price" style={{ marginLeft: '8px', textDecoration: 'line-through', color: '#999' }}>
                                  ${product.original_price}
                                </span>
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  {message.products.length > 3 && (
                    <div className="chatbot-more-products">
                      and {message.products.length - 3} more products...
                    </div>
                  )}
                </div>
              )}
              
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
            placeholder={isListening ? "Listening..." : "Type your message..."}
            className="chatbot-input"
            maxLength={500}
          />
          <button 
            type="button" 
            className={`chatbot-voice-btn ${isListening ? 'listening' : ''}`}
            onClick={toggleVoiceRecording}
            title={isListening ? "Stop recording" : "Start voice recording"}
          >
            <FontAwesomeIcon 
              icon={isListening ? faMicrophoneSlash : faMicrophone} 
              className={isListening ? 'recording' : ''}
            />
          </button>
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
