export const handleVoiceStart = (recognition: any, setIsListening: (value: boolean) => void) => {
  if (recognition) {
    try {
      recognition.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error starting voice recognition:', error);
      setIsListening(false);
    }
  }
};

export const handleVoiceStop = (recognition: any, setIsListening: (value: boolean) => void) => {
  if (recognition) {
    recognition.stop();
    setIsListening(false);
  }
};

export const toggleVoiceRecognition = (
  isListening: boolean,
  recognition: any,
  setIsListening: (value: boolean) => void
) => {
  if (isListening) {
    handleVoiceStop(recognition, setIsListening);
  } else {
    handleVoiceStart(recognition, setIsListening);
  }
};
