import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone, faStop, faUpload, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { aiService, ConversationMessage } from '../../services/aiService';
import { Product } from '../../contexts/ShopContext';
import './Chatbot.css';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  products?: Product[];
  isHtml?: boolean;
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
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]);
  const [lastFunctionUsed, setLastFunctionUsed] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Function to get icon and title based on rec_source
  const getRecommendationIcon = (source: string) => {
    switch (source) {
      case 'personalized':
        return { icon: '👤', title: 'Personalized Recommendation' };
      case 'category':
        return { icon: '📂', title: 'Category Based' };
      case 'trending':
        return { icon: '🔥', title: 'Trending Product' };
      case 'rating':
        return { icon: '⭐', title: 'Top Rated' };
      case 'description':
        return { icon: '📝', title: 'Description Match' };
      case 'wishlist':
        return { icon: '💖', title: 'Wishlist Suggestion' };
      case 'purchase':
        return { icon: '🛒', title: 'Purchase History Based' };
      case 'same_taste':
        return { icon: '🤝', title: 'Similar Taste' };
      case 'product':
        return { icon: '🛍️', title: 'Similarity Search' };
      case 'gift':
        return { icon: '🎁', title: 'Gift Suggestion' };
      default:
        return null;
    }
  };

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

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/ai/search-by-voice`, {
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
            description: product.description,
            rec_source: product.rec_source // Add rec_source field!
          }));

          setLastSearchResults(products);
          setLastSearchQuery(voiceResponse.transcribed_text || '');
          
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

          const voiceSearchMessage: Message = {
            id: Date.now() + 1,
            text: responseText,
            isUser: false,
            timestamp: new Date(),
            products: products.slice(0, 3),
            isHtml: true
          };

          setMessages(prev => [...prev, voiceSearchMessage]);

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
                isUser: false,
                timestamp: new Date()
              };
              setMessages(prev => [...prev, showAllMessage]);
            }, 1000);
          }
        } else {
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
        // const showAllMessage: Message = {
        //   id: Date.now() + 1,
        //   text: `Perfect! I'll show you all ${lastSearchResults.length} results on the search results page.`,
        //   isUser: false,
        //   timestamp: new Date()
        // };
        
        // setMessages(prev => [...prev, showAllMessage]);
        
        // Store search results in sessionStorage for the SearchResult page
        sessionStorage.setItem('chatbotSearchResults', JSON.stringify(lastSearchResults));
        sessionStorage.setItem('chatbotSearchQuery', lastSearchQuery);
        
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
        }, 1500);
        
        return;
      }

      const aiResponse = await aiService.searchProducts({
        messages: [...conversationHistory, { role: "user", content: messageText }],
        limit: 10
      });

      console.log('AI search response:', aiResponse);

      if (aiResponse.status === 'success' && aiResponse.products && aiResponse.products.length > 0) {
        const products = aiService.convertToProducts(aiResponse.products);
        setLastSearchResults(products);
        setLastSearchQuery(messageText);
        
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
        
        const aiSearchMessage: Message = {
          id: Date.now() + 1,
          text: responseText,
          isUser: false,
          timestamp: new Date(),
          products: products.slice(0, 3),
          isHtml: true
        };
        
        setMessages(prev => [...prev, aiSearchMessage]);

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
              isUser: false,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, moreResultsMessage]);
          }, 1000);
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
        
        const botResponse: Message = {
          id: Date.now() + 1,
          text: errorMessage,
          isUser: false,
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
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    } finally {
      setIsTyping(false);
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
        </div>

        <div className="chatbot-messages">
          {messages.map((message) => (
            <div key={message.id} className={`chatbot-message ${message.isUser ? 'user' : 'bot'}`}>
              <div className="chatbot-message-content">
                {message.isHtml ? (
                  <div dangerouslySetInnerHTML={{ __html: message.text }} />
                ) : (
                  message.text
                )}
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
                            {/* Recommendation icon based on rec_source */}
                            <div className="product-function-icon">
                              {(() => {
                                const recommendationData = product.rec_source ? getRecommendationIcon(product.rec_source) : null;
                                if (recommendationData) {
                                  return (
                                    <div 
                                      className="recommendation-icon" 
                                      title={recommendationData.title}
                                      style={{
                                        background: '#fff',
                                        borderRadius: '50%',
                                        width: '22px',
                                        height: '22px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '14px',
                                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.18)',
                                        border: '2.5px solid #fff',
                                        cursor: 'help',
                                        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                                        position: 'absolute',
                                        top: '-8px',
                                        right: '-8px',
                                        zIndex: 100
                                      }}
                                      onMouseEnter={(e) => {
                                        e.currentTarget.style.transform = 'scale(1.2)';
                                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
                                      }}
                                      onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = 'scale(1)';
                                        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.18)';
                                      }}
                                    >
                                      {recommendationData.icon}
                                    </div>
                                  );
                                }
                                // Fallback to old function-based icons
                                return lastFunctionUsed === 'find_gifts' ? (
                                  <span className="gift-icon" title="Gift Suggestion">🎁</span>
                                ) : (
                                  <span className="product-icon" title="Product Search">🛍️</span>
                                );
                              })()}
                            </div>                          <img src={product.imageUrl} alt={product.name} className="chatbot-product-image" />
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
                          
                          // Store the function type for dynamic title and icon display
                          if (lastFunctionUsed === 'find_gifts') {
                            sessionStorage.setItem('searchResultTitle', 'Search Gift Result');
                            sessionStorage.setItem('searchFunctionType', 'find_gifts');
                          } else {
                            sessionStorage.setItem('searchResultTitle', 'Search Product Result');
                            sessionStorage.setItem('searchFunctionType', 'find_products');
                          }
                          
                          // Verify storage
                          const stored = sessionStorage.getItem('chatbotSearchResults');
                          console.log('✅ Verified storage:', stored ? JSON.parse(stored).length : 'null');
                          
                          // Navigate to dedicated search results page
                          navigate(`/search-results?t=${Date.now()}`);
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
