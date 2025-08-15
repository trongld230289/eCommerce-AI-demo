// Simple transcription service (returns English text for AI)
export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const result = await transcribeAudioWithTranslation(audioBlob);
  return result.chatbotText; // Return English text for AI
}

// Enhanced transcription service that returns both original and translated text
export async function transcribeAudioWithTranslation(audioBlob: Blob): Promise<{
  displayText: string;
  chatbotText: string;
  wasTranslated: boolean;
}> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.webm');
  
  try {
    const response = await fetch('http://localhost:5005/transcribe-and-translate', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Transcription API error:', errorData);
      throw new Error(`Transcription failed: ${errorData.error || 'Unknown error'}`);
    }
    
    const data = await response.json();
    
    return {
      displayText: data.original_text, // Show Vietnamese to user
      chatbotText: data.final_text,    // Send English to AI
      wasTranslated: data.detected_language === 'vi'
    };
  } catch (error) {
    console.error('Transcription error:', error);
    throw error;
  }
}

// Check if the Whisper API service is available
export async function checkServiceStatus(): Promise<any> {
  try {
    const response = await fetch('http://localhost:5005/status');
    return await response.json();
  } catch (error) {
    console.error('Service status check failed:', error);
    throw error;
  }
}
