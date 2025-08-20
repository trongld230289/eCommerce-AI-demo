import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone, faStop, faUpload, faSpinner } from '@fortawesome/free-solid-svg-icons';
<<<<<<< HEAD
import { aiService } from '../../services/aiService';
=======
import { aiService, ConversationMessage } from '../../services/aiService';
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
import { Product } from '../../contexts/ShopContext';
import './Chatbot.css';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  products?: Product[];
<<<<<<< HEAD
=======
  isHtml?: boolean;
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
}

interface ChatbotProps {
  isVisible: boolean;
  onClose: () => void;
}

const Chatbot: React.FC<ChatbotProps> = ({ isVisible, onClose }) => {
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
  const [lastSearchResults, setLastSearchResults] = useState<Product[]>([]);
  const [lastSearchQuery, setLastSearchQuery] = useState<string>('');
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [showVoiceOptions, setShowVoiceOptions] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
<<<<<<< HEAD
=======
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]);
  const [lastFunctionUsed, setLastFunctionUsed] = useState<string>('');
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {}, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // ---- FIX: pick best MIME per browser; don't force-convert on client
  const chooseMime = (): string => {
    if (typeof MediaRecorder !== 'undefined') {
      if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) return "audio/webm;codecs=opus"; // Chrome/Edge
      if (MediaRecorder.isTypeSupported("audio/webm")) return "audio/webm";
      if (MediaRecorder.isTypeSupported("audio/mp4")) return "audio/mp4"; // Safari/iOS
      if (MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")) return "audio/ogg;codecs=opus"; // Firefox
    }
    return ""; // let browser decide
  };

  // ---- Voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = chooseMime();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      const chunks: Blob[] = [];
      recorder.ondataavailable = (event) => event.data.size && chunks.push(event.data);

      recorder.onstop = async () => {
        setIsRecording(false);
        stream.getTracks().forEach(track => track.stop());

        // FIX: keep original format, set correct extension based on actual MIME
        const blobType = recorder.mimeType || chunks[0]?.type || "audio/webm";
        const ext = blobType.includes("mp4") ? "m4a"
                 : blobType.includes("webm") ? "webm"
                 : blobType.includes("ogg") ? "ogg"
                 : blobType.includes("mpeg") ? "mp3"
                 : blobType.includes("wav") ? "wav"
                 : "webm";

        const audioBlob = new Blob(chunks, { type: blobType });
        const file = new File([audioBlob], `recording.${ext}`, { type: blobType });

        await processVoiceSearch(file); // send original file; no client-side WAV conversion
      };

      setMediaRecorder(recorder);
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      addMessage('Sorry, I couldn\'t access your microphone. Please check your browser permissions.', false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
    }
  };

  // ---- FIX: simplified; send original file/blob as-is; field name = 'file'
  const processVoiceSearch = async (fileOrBlob: File | Blob) => {
    setIsTyping(true);
    setIsProcessingVoice(true);
    try {
      let file: File;
      if (fileOrBlob instanceof File) {
        file = fileOrBlob;
      } else {
        const type = fileOrBlob.type || "audio/webm";
        const ext = type.includes("mp4") ? "m4a"
                 : type.includes("webm") ? "webm"
                 : type.includes("ogg") ? "ogg"
                 : type.includes("mpeg") ? "mp3"
                 : type.includes("wav") ? "wav"
                 : "webm";
        file = new File([fileOrBlob], `recording.${ext}`, { type });
      }

      const formData = new FormData();
      formData.append('audio', file);            // <--- IMPORTANT: 'audio' to match backend
      formData.append('language', 'vi');        // optional but helpful

<<<<<<< HEAD
      const response = await fetch('http://localhost:8000/api/ai/search-by-voice', {
=======
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/ai/search-by-voice`, {
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        method: 'POST',
        body: formData
      });

      const voiceResponse = await response.json();
      console.log('Voice search response:', voiceResponse);

      if (voiceResponse.status === 'success') {
        if (voiceResponse.transcribed_text) {
          const transcriptMessage: Message = {
            id: Date.now(),
            text: `🎤 "${voiceResponse.transcribed_text}"`,
            isUser: true,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, transcriptMessage]);
        }

        if (voiceResponse.products && voiceResponse.products.length > 0) {
          const products = voiceResponse.products.map((product: any) => ({
            id: product.id,
            name: product.name,
            price: product.price,
            original_price: product.original_price,
            category: product.category,
            imageUrl: product.imageUrl || product.image_url,
            description: product.description
          }));

          setLastSearchResults(products);
          setLastSearchQuery(voiceResponse.transcribed_text || '');
<<<<<<< HEAD

          let responseText = `🎤 Voice search completed! I found ${voiceResponse.total_results} products`;
          if (voiceResponse.transcribed_text) {
            responseText += ` for "${voiceResponse.transcribed_text}"`;
          }
          responseText += '.\n\nHere are the top results:';
=======
          
          // Update function used tracking
          if (voiceResponse.function_used) {
            setLastFunctionUsed(voiceResponse.function_used);
          }

          // Build response text based on whether we have products (same logic as text search)
          let responseText = '';
          
          if (voiceResponse.products && voiceResponse.products.length > 0) {
            // If we have products, only show intro + header
            if (voiceResponse.intro) {
              responseText += voiceResponse.intro.replace(/\n/g, '<br>');
            }
            
            if (voiceResponse.header) {
              if (responseText) responseText += '<br><br>';
              responseText += voiceResponse.header.replace(/\n/g, '<br>');
            }
          } else {
            // If no products, get assistant message content (no intro/header)
            if (voiceResponse.messages && voiceResponse.messages.length > 0) {
              const latestAssistantMessage = [...voiceResponse.messages]
                .reverse()
                .find(msg => msg.role === 'assistant');
              
              if (latestAssistantMessage && latestAssistantMessage.content) {
                responseText = latestAssistantMessage.content.replace(/\n/g, '<br>');
              }
            }
          }
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

          const voiceSearchMessage: Message = {
            id: Date.now() + 1,
            text: responseText,
            isUser: false,
            timestamp: new Date(),
<<<<<<< HEAD
            products: products.slice(0, 3)
=======
            products: products.slice(0, 3),
            isHtml: true
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
          };

          setMessages(prev => [...prev, voiceSearchMessage]);

<<<<<<< HEAD
          if (products.length > 3) {
            setTimeout(() => {
              const showAllMessage: Message = {
                id: Date.now() + 2,
                text: `Would you like to see all ${products.length} results on the products page?`,
=======
          // Update conversation history from voice response
          if (voiceResponse.messages && voiceResponse.messages.length > 0) {
            const backendConversationHistory: ConversationMessage[] = voiceResponse.messages.map((msg: any) => ({
              role: msg.role,
              content: msg.content
            }));
            setConversationHistory(backendConversationHistory);
          }

          if (products.length > 3) {
            setTimeout(() => {
              // Create language-appropriate message for voice search too
              let moreResultsText = `Would you like to see all ${products.length} results on the products page?`;
              
              // If language detected is Vietnamese, use Vietnamese message
              if (voiceResponse.language_detected === 'vi') {
                moreResultsText = `Bạn có muốn tôi hiển thị tất cả ${products.length} kết quả trên trang sản phẩm không?`;
              }
              
              const showAllMessage: Message = {
                id: Date.now() + 2,
                text: moreResultsText,
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
                isUser: false,
                timestamp: new Date()
              };
              setMessages(prev => [...prev, showAllMessage]);
            }, 1000);
          }
        } else {
<<<<<<< HEAD
          addMessage('🎤 I heard you, but couldn\'t find any products matching your voice search. Please try again.', false);
=======
          // Handle no products case for voice search  
          let errorMessage = '';
          if (voiceResponse.messages && voiceResponse.messages.length > 0) {
            // Find the latest assistant message
            const latestAssistantMessage = [...voiceResponse.messages]
              .reverse()
              .find((msg: any) => msg.role === 'assistant');
            
            if (latestAssistantMessage && latestAssistantMessage.content) {
              errorMessage = latestAssistantMessage.content.replace(/\n/g, '<br>');
            }
          }
          
          // Fallback to intro if no messages available
          if (!errorMessage && voiceResponse.intro) {
            errorMessage = voiceResponse.intro.replace(/\n/g, '<br>');
          }
          
          // Final fallback
          if (!errorMessage) {
            errorMessage = '🎤 I heard you, but couldn\'t find any products matching your voice search. Please try again.';
          }
          
          addMessage(errorMessage, false);
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        }
      } else {
        addMessage('🎤 Sorry, I had trouble processing your voice search. Please try again.', false);
      }
    } catch (error) {
      console.error('Voice search error:', error);
      let errorMessage = '🎤 There was an error processing your voice search. Please try again.';
      if (error instanceof Error) {
        if (error.message.includes('network') || error.message.includes('fetch')) {
          errorMessage = '🎤 Network error. Please check your connection and try again.';
        } else if (error.message.includes('format') || error.message.includes('file')) {
          errorMessage = '🎤 Audio format error. Your browser might not be compatible with voice recording.';
        } else if (error.message.includes('permission') || error.message.includes('microphone')) {
          errorMessage = '🎤 Microphone permission denied. Please allow microphone access and try again.';
        }
      }
      addMessage(errorMessage, false);
    } finally {
      setIsTyping(false);
      setIsProcessingVoice(false);
    }
  };

  // ---- Upload: keep original file; don't rename to .wav
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type.startsWith('audio/')) {
        if (file.size <= 25 * 1024 * 1024) { // 25MB limit
          processVoiceSearch(file);
        } else {
          addMessage('Audio file is too large. Please upload a file smaller than 25MB.', false);
        }
      } else {
        addMessage('Please upload an audio file (webm, m4a, mp3, ogg, wav, flac).', false);
      }
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const addMessage = (text: string, isUser: boolean, products?: Product[]) => {
    const message: Message = {
      id: Date.now(),
      text,
      isUser,
      timestamp: new Date(),
      products
    };
    setMessages(prev => [...prev, message]);
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

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageText = inputValue;
    setInputValue('');
    setIsTyping(true);

    try {
      const isShowAllRequest = (inputValue.toLowerCase().includes('show all') || 
                               inputValue.toLowerCase().includes('see all') ||
                               inputValue.toLowerCase().includes('view all') ||
                               (inputValue.toLowerCase().includes('yes') && lastSearchResults.length > 0));
      
      if (isShowAllRequest && lastSearchResults.length > 0) {
<<<<<<< HEAD
        const showAllMessage: Message = {
          id: Date.now() + 1,
          text: `Perfect! I'll show you all ${lastSearchResults.length} results on the search results page.`,
          isUser: false,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, showAllMessage]);
=======
        // const showAllMessage: Message = {
        //   id: Date.now() + 1,
        //   text: `Perfect! I'll show you all ${lastSearchResults.length} results on the search results page.`,
        //   isUser: false,
        //   timestamp: new Date()
        // };
        
        // setMessages(prev => [...prev, showAllMessage]);
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        
        // Store search results in sessionStorage for the SearchResult page
        sessionStorage.setItem('chatbotSearchResults', JSON.stringify(lastSearchResults));
        sessionStorage.setItem('chatbotSearchQuery', lastSearchQuery);
        
<<<<<<< HEAD
        setTimeout(() => {
          navigate('/search-results');
=======
        // Store the function type for dynamic title and icon display
        if (lastFunctionUsed === 'find_gifts') {
          sessionStorage.setItem('searchResultTitle', 'Search Gift Result');
          sessionStorage.setItem('searchFunctionType', 'find_gifts');
        } else {
          sessionStorage.setItem('searchResultTitle', 'Search Product Result');
          sessionStorage.setItem('searchFunctionType', 'find_products');
        }
        
        setTimeout(() => {
          navigate(`/search-results?t=${Date.now()}`);
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        }, 1500);
        
        return;
      }

      const aiResponse = await aiService.searchProducts({
<<<<<<< HEAD
        query: messageText,
=======
        messages: [...conversationHistory, { role: "user", content: messageText }],
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        limit: 10
      });

      console.log('AI search response:', aiResponse);

      if (aiResponse.status === 'success' && aiResponse.products && aiResponse.products.length > 0) {
        const products = aiService.convertToProducts(aiResponse.products);
        setLastSearchResults(products);
        setLastSearchQuery(messageText);
        
<<<<<<< HEAD
        let responseText = `I found ${aiResponse.total_results} products for "${messageText}".`;
        if (aiResponse.search_intent) {
          const intent = aiResponse.search_intent;
          const appliedFilters: string[] = [];
          if (intent.filters.category) appliedFilters.push(`Category: ${intent.filters.category}`);
          if (intent.filters.min_price || intent.filters.max_price) {
            const priceRange: string[] = [];
            if (intent.filters.min_price) priceRange.push(`min $${intent.filters.min_price}`);
            if (intent.filters.max_price) priceRange.push(`max $${intent.filters.max_price}`);
            appliedFilters.push(`Price: ${priceRange.join(', ')}`);
          }
          if (intent.filters.min_rating) appliedFilters.push(`Min rating: ${intent.filters.min_rating} stars`);
          if (intent.filters.min_discount) appliedFilters.push(`Min discount: ${intent.filters.min_discount}%`);
          if (appliedFilters.length > 0) responseText += `\n\nI detected these filters: ${appliedFilters.join(', ')}`;
        }
        responseText += `\n\nHere are the top results:`;
=======
        // Check if function switched and clear conversation history if needed
        if (aiResponse.function_used && lastFunctionUsed && aiResponse.function_used !== lastFunctionUsed) {
          setConversationHistory([]);
          console.log(`🔄 Function switched from ${lastFunctionUsed} to ${aiResponse.function_used}. Conversation history cleared.`);
        }
        setLastFunctionUsed(aiResponse.function_used || '');
        
        // Build response text based on whether we have products
        let responseText = '';
        
        if (aiResponse.products && aiResponse.products.length > 0) {
          // If we have products, only show intro + header
          if (aiResponse.intro) {
            responseText += aiResponse.intro.replace(/\n/g, '<br>');
          }
          
          if (aiResponse.header) {
            if (responseText) responseText += '<br><br>';
            responseText += aiResponse.header.replace(/\n/g, '<br>');
          }
        } else {
          // If no products, get assistant message content (no intro/header)
          if (aiResponse.messages && aiResponse.messages.length > 0) {
            const latestAssistantMessage = [...aiResponse.messages]
              .reverse()
              .find(msg => msg.role === 'assistant');
            
            if (latestAssistantMessage && latestAssistantMessage.content) {
              responseText = latestAssistantMessage.content.replace(/\n/g, '<br>');
            }
          }
        }
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        
        const aiSearchMessage: Message = {
          id: Date.now() + 1,
          text: responseText,
          isUser: false,
          timestamp: new Date(),
<<<<<<< HEAD
          products: products.slice(0, 3)
=======
          products: products.slice(0, 3),
          isHtml: true
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        };
        
        setMessages(prev => [...prev, aiSearchMessage]);

<<<<<<< HEAD
        if (products.length > 3) {
          setTimeout(() => {
            const moreResultsMessage: Message = {
              id: Date.now() + 2,
              text: `I found ${products.length} total results. Would you like me to show you all of them on the products page?`,
=======
        // Update conversation history from backend messages
        if (aiResponse.messages && aiResponse.messages.length > 0) {
          // Use the complete conversation history from backend
          const backendConversationHistory: ConversationMessage[] = aiResponse.messages.map(msg => ({
            role: msg.role,
            content: msg.content
          }));
          setConversationHistory(backendConversationHistory);
        }

        // Use show_all_product message from backend if available
        console.log('🔍 Checking show_all_product:', {
          show_all_product: aiResponse.show_all_product,
          type: typeof aiResponse.show_all_product,
          length: aiResponse.show_all_product?.length,
          products_count: products.length,
          raw_value: JSON.stringify(aiResponse.show_all_product)
        });
        
        // More relaxed check - just need truthy value with content
        if (aiResponse.show_all_product && String(aiResponse.show_all_product).trim().length > 0) {
          console.log('✅ Using backend show_all_product message');
          setTimeout(() => {
            const moreResultsMessage: Message = {
              id: Date.now() + 2,
              text: String(aiResponse.show_all_product).trim(),
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
              isUser: false,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, moreResultsMessage]);
          }, 1000);
<<<<<<< HEAD
        }
      } else {
        const errorMessage = aiResponse.message || 'I couldn\'t find any products matching your request. Could you try rephrasing your search?';
=======
        } else if (products.length > 3) {
          // Fallback: create our own "show all" message if backend doesn't provide one
          console.log('⚠️ Backend did not provide show_all_product, creating fallback message');
          setTimeout(() => {
            const fallbackMessage: Message = {
              id: Date.now() + 2,
              text: `Would you like to see all ${products.length} results on the products page?`,
              isUser: false,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, fallbackMessage]);
          }, 1000);
        }
      } else {
        // For no-products case: get assistant message content (no intro/header)
        let errorMessage = '';
        if (aiResponse.messages && aiResponse.messages.length > 0) {
          // Find the latest assistant message
          const latestAssistantMessage = [...aiResponse.messages]
            .reverse()
            .find(msg => msg.role === 'assistant');
          
          if (latestAssistantMessage && latestAssistantMessage.content) {
            errorMessage = latestAssistantMessage.content.replace(/\n/g, '<br>');
          }
        }
        
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        const botResponse: Message = {
          id: Date.now() + 1,
          text: errorMessage,
          isUser: false,
<<<<<<< HEAD
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botResponse]);
      }
    } catch (error) {
      console.error('Error with AI search:', error);
      const botResponse: Message = {
        id: Date.now() + 1,
        text: getBotResponse(messageText),
=======
          timestamp: new Date(),
          isHtml: true
        };
        setMessages(prev => [...prev, botResponse]);
        
        // Update conversation history for error case too
        if (aiResponse.messages && aiResponse.messages.length > 0) {
          // Use the complete conversation history from backend
          const backendConversationHistory: ConversationMessage[] = aiResponse.messages.map(msg => ({
            role: msg.role,
            content: msg.content
          }));
          setConversationHistory(backendConversationHistory);
        }
      }
    } catch (error) {
      console.error('Error with AI search:', error);
      
      const errorMessage = 'I encountered an issue while searching. Let me try to help you in another way. Could you please rephrase your question or try asking about specific products?';
      
      const botResponse: Message = {
        id: Date.now() + 1,
        text: errorMessage,
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    } finally {
      setIsTyping(false);
    }
  };

<<<<<<< HEAD
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

=======
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
  if (!isVisible) return null;

  return (
    <div className="chatbot-overlay">
      <div className="chatbot-container">
        <div className="chatbot-header">
          <div className="chatbot-header-info">
            <div className="chatbot-avatar">🤖</div>
            <div className="chatbot-header-text">
              <h4>Electro Assistant</h4>
<<<<<<< HEAD
              <span className="chatbot-status">Online</span>
            </div>
          </div>
          <button className="chatbot-close-btn" onClick={onClose}>
            ✕
          </button>
=======
              <span className="chatbot-status">
                Online {conversationHistory.length > 0 && `• ${Math.floor(conversationHistory.length/2)} exchanges`}
              </span>
            </div>
          </div>
          <div className="chatbot-header-actions">
            {conversationHistory.length > 0 && (
              <button 
                className="chatbot-clear-btn" 
                onClick={() => {
                  setConversationHistory([]);
                  setLastFunctionUsed('');
                  addMessage('🔄 Conversation context cleared. Starting fresh!', false);
                }}
                title="Clear conversation history"
              >
                🔄
              </button>
            )}
            <button className="chatbot-close-btn" onClick={onClose}>
              ✕
            </button>
          </div>
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        </div>

        <div className="chatbot-messages">
          {messages.map((message) => (
            <div key={message.id} className={`chatbot-message ${message.isUser ? 'user' : 'bot'}`}>
              <div className="chatbot-message-content">
<<<<<<< HEAD
                {message.text}
=======
                {message.isHtml ? (
                  <div dangerouslySetInnerHTML={{ __html: message.text }} />
                ) : (
                  message.text
                )}
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
              </div>

              {message.products && message.products.length > 0 && (
                <div className="chatbot-products">
                  <div className="chatbot-products-grid">
                    {message.products.slice(0, 3).map((product) => (
                      <div key={product.id} className="chatbot-product-item">
                        <div 
                          className="chatbot-product-card"
                          onClick={() => navigate(`/product/${product.id}`)}
                          style={{ cursor: 'pointer' }}
                        >
<<<<<<< HEAD
=======
                          {/* Function type icon */}
                          <div className="product-function-icon">
                            {lastFunctionUsed === 'find_gifts' ? (
                              <span className="gift-icon" title="Gift Suggestion">🎁</span>
                            ) : (
                              <span className="product-icon" title="Product Search">🛍️</span>
                            )}
                          </div>
                          
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
                          <img src={product.imageUrl} alt={product.name} className="chatbot-product-image" />
                          <div className="chatbot-product-info">
                            <h4 className="chatbot-product-name">{product.name}</h4>
                            <p className="chatbot-product-category">{product.category}</p>
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
                      <p>Found {message.products.length} products total.</p>
                      <button 
                        className="chatbot-view-all-btn"
                        onClick={() => {
                          if (!message.products) return;
                          console.log('🚀 View All button clicked!');
                          console.log('📦 Storing products:', message.products.length, message.products);
                          console.log('🔍 Last search query:', lastSearchQuery);
                          
                          // Store search results in sessionStorage for the SearchResult page
                          sessionStorage.setItem('chatbotSearchResults', JSON.stringify(message.products));
                          sessionStorage.setItem('chatbotSearchQuery', lastSearchQuery);
                          
<<<<<<< HEAD
=======
                          // Store the function type for dynamic title and icon display
                          if (lastFunctionUsed === 'find_gifts') {
                            sessionStorage.setItem('searchResultTitle', 'Search Gift Result');
                            sessionStorage.setItem('searchFunctionType', 'find_gifts');
                          } else {
                            sessionStorage.setItem('searchResultTitle', 'Search Product Result');
                            sessionStorage.setItem('searchFunctionType', 'find_products');
                          }
                          
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
                          // Verify storage
                          const stored = sessionStorage.getItem('chatbotSearchResults');
                          console.log('✅ Verified storage:', stored ? JSON.parse(stored).length : 'null');
                          
                          // Navigate to dedicated search results page
<<<<<<< HEAD
                          navigate('/search-results');
=======
                          navigate(`/search-results?t=${Date.now()}`);
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
                        }}
                      >
                        View All {message.products.length} Results
                      </button>
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
                {isProcessingVoice ? (
                  <div className="chatbot-voice-processing">
                    🎤 Processing your voice search...
                    <div className="chatbot-typing">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                ) : (
                  <div className="chatbot-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                )}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {showVoiceOptions && (
          <div className="chatbot-voice-options">
            <div className="voice-options-header">
              <h4>Voice Search Options</h4>
              <button 
                onClick={() => setShowVoiceOptions(false)}
                className="voice-options-close"
              >
                ✕
              </button>
            </div>
            <div className="voice-options-content">
              <div className="voice-option">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`voice-record-btn ${isRecording ? 'recording' : ''} ${isProcessingVoice ? 'processing' : ''}`}
                  disabled={isProcessingVoice}
                >
                  <FontAwesomeIcon 
                    icon={isProcessingVoice ? faSpinner : (isRecording ? faStop : faMicrophone)} 
                    spin={isProcessingVoice}
                  />
                  {isProcessingVoice ? 'Processing...' : (isRecording ? 'Stop Recording' : 'Start Recording')}
                </button>
                {isRecording && (
                  <div className="recording-indicator">
                    <div className="recording-pulse"></div>
                    🎤 Recording... (click Stop to finish)
                  </div>
                )}
              </div>

              <div className="voice-option-divider">OR</div>

              <div className="voice-option">
                <label htmlFor="audio-upload" className="voice-upload-btn">
                  <FontAwesomeIcon icon={faUpload} />
                  Upload Audio File
                </label>
                <input
                  id="audio-upload"
                  type="file"
                  accept="audio/*,.webm,.m4a,.mp3,.ogg,.wav,.flac"  // FIX: include common formats
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  ref={fileInputRef}
                />
                <small className="voice-upload-note">
                  Supports: WEBM, M4A/MP4, MP3, OGG, WAV, FLAC (max 25MB)
                </small>
              </div>
            </div>
          </div>
        )}

        <form className="chatbot-input-form" onSubmit={sendMessage}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="chatbot-input"
            maxLength={500}
          />
          <button 
            type="button" 
            className={`chatbot-voice-btn ${showVoiceOptions ? 'active' : ''}`}
            onClick={() => setShowVoiceOptions(!showVoiceOptions)}
            title="Voice search options"
          >
            <FontAwesomeIcon icon={faMicrophone} />
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
