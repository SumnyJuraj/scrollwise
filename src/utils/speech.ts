export let isSpeaking = false;

export const getIsSpeaking = (): boolean => isSpeaking;

export const speakFact = (
  text: string,
  onStart?: () => void,
  onEnd?: () => void
): (() => void) => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return () => {};
  }

  // Ak už beží čítanie, zastavíme ho
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;

  // Search for English voice, fallback to system default
  const voices = window.speechSynthesis.getVoices();
  const preferredVoice =
    voices.find((v) => v.lang === 'en-US') ||
    voices.find((v) => v.lang === 'en-GB') ||
    voices.find((v) => v.lang.startsWith('en')) ||
    null;

  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  utterance.onstart = () => {
    isSpeaking = true;
    onStart?.();
  };

  utterance.onend = () => {
    isSpeaking = false;
    onEnd?.();
  };

  utterance.onerror = () => {
    isSpeaking = false;
    onEnd?.();
  };

  window.speechSynthesis.speak(utterance);

  return () => {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    onEnd?.();
  };
};

export const stopSpeech = () => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
  }
};
