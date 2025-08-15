// Frontend Integration Example for Enhanced Whisper API with Translation
// =====================================================================

// Example 1: Basic transcription with optional translation
async function transcribeAudio(audioBlob, includeTranslation = true) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    
    if (includeTranslation) {
        formData.append('translate', 'true');
    }
    
    try {
        const response = await fetch('http://localhost:5005/transcribe', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        /*
        Response structure:
        {
            "text": "Tôi muốn mua áo sơ mi",
            "language": "vi",
            "translated_text": "I want to buy a shirt",
            "translation_available": true
        }
        */
        
        return result;
    } catch (error) {
        console.error('Transcription failed:', error);
        throw error;
    }
}

// Example 2: Automatic transcription + translation (recommended for chatbot)
async function transcribeAndTranslateForChatbot(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    
    try {
        const response = await fetch('http://localhost:5005/transcribe-and-translate', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        /*
        Response structure:
        {
            "original_text": "Tôi muốn tìm điện thoại iPhone",
            "detected_language": "vi",
            "translated_text": "I want to find iPhone phones",
            "final_text": "I want to find iPhone phones"
        }
        */
        
        // Use final_text for chatbot processing
        return {
            displayText: result.original_text, // Show Vietnamese to user
            chatbotInput: result.final_text,   // Send English to AI
            isTranslated: result.detected_language === 'vi'
        };
    } catch (error) {
        console.error('Transcription and translation failed:', error);
        throw error;
    }
}

// Example 3: Text-only translation
async function translateText(vietnameseText) {
    try {
        const response = await fetch('http://localhost:5005/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: vietnameseText
            })
        });
        
        const result = await response.json();
        
        /*
        Response structure:
        {
            "original_text": "Tôi muốn tìm sản phẩm điện thoại",
            "translated_text": "I want to find phone products",
            "detected_language": "vi"
        }
        */
        
        return result;
    } catch (error) {
        console.error('Translation failed:', error);
        throw error;
    }
}

// Example 4: Complete voice chat integration
class VietnamesesVoiceChatbot {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            
            const audioChunks = [];
            this.mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                await this.processVoiceInput(audioBlob);
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            console.log('Recording started...');
        } catch (error) {
            console.error('Failed to start recording:', error);
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            console.log('Recording stopped...');
        }
    }
    
    async processVoiceInput(audioBlob) {
        try {
            // Step 1: Transcribe and translate Vietnamese speech
            const transcriptionResult = await transcribeAndTranslateForChatbot(audioBlob);
            
            // Step 2: Display original Vietnamese text to user
            this.displayUserMessage(transcriptionResult.displayText, transcriptionResult.isTranslated);
            
            // Step 3: Send English text to chatbot API
            const chatbotResponse = await this.sendToChatbot(transcriptionResult.chatbotInput);
            
            // Step 4: Display chatbot response
            this.displayBotMessage(chatbotResponse);
            
        } catch (error) {
            console.error('Voice processing failed:', error);
            this.displayErrorMessage('Sorry, I could not understand your voice input.');
        }
    }
    
    async sendToChatbot(englishText) {
        // Send the English text to your existing chatbot API
        try {
            const response = await fetch('http://localhost:8002/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: englishText,
                    user_id: 'current_user'
                })
            });
            
            const result = await response.json();
            return result.response;
        } catch (error) {
            console.error('Chatbot API failed:', error);
            return 'Sorry, I could not process your request right now.';
        }
    }
    
    displayUserMessage(text, wasTranslated) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'user-message';
        messageDiv.innerHTML = `
            <div class="message-content">${text}</div>
            ${wasTranslated ? '<small class="translation-note">🌐 Translated from Vietnamese</small>' : ''}
        `;
        document.getElementById('chat-container').appendChild(messageDiv);
    }
    
    displayBotMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'bot-message';
        messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
        document.getElementById('chat-container').appendChild(messageDiv);
    }
    
    displayErrorMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'error-message';
        messageDiv.innerHTML = `<div class="message-content">❌ ${text}</div>`;
        document.getElementById('chat-container').appendChild(messageDiv);
    }
}

// Usage example:
// const voiceChatbot = new VietnamesesVoiceChatbot();
// 
// document.getElementById('record-button').addEventListener('mousedown', () => {
//     voiceChatbot.startRecording();
// });
// 
// document.getElementById('record-button').addEventListener('mouseup', () => {
//     voiceChatbot.stopRecording();
// });

export { 
    transcribeAudio, 
    transcribeAndTranslateForChatbot, 
    translateText, 
    VietnamesesVoiceChatbot 
};
