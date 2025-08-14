import React from 'react';
import './Chatbot.css';

interface ChatbotIconProps {
  onClick: () => void;
  isVisible: boolean;
}

const ChatbotIcon: React.FC<ChatbotIconProps> = ({ onClick, isVisible }) => {
  if (isVisible) return null; // Hide icon when chatbot is open

  return (
    <button className="chatbot-float-btn" onClick={onClick} title="Chat with us">
      💬
    </button>
  );
};

export default ChatbotIcon;
