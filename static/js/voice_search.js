document.getElementById("voice-open").addEventListener("click", () => document.getElementById("voice-dialog").showModal());
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recordButton = document.getElementById("voice-record");
const voiceStatus = document.getElementById("voice-status");
if (!SpeechRecognition) {
  recordButton.disabled = true;
  voiceStatus.textContent = "Voice recognition is unavailable here. Type a simulated transcript to try voice search.";
} else {
  recordButton.addEventListener("click", () => {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.onstart = () => { recordButton.disabled = true; voiceStatus.textContent = "Listening…"; };
    recognition.onresult = event => {
      document.getElementById("transcript").value = event.results[0][0].transcript;
      voiceStatus.textContent = "Transcript ready. Review it and search.";
    };
    recognition.onerror = () => { voiceStatus.textContent = "Microphone recognition failed. You can type a simulated transcript below."; };
    recognition.onend = () => { recordButton.disabled = false; };
    try { recognition.start(); }
    catch { recordButton.disabled = false; voiceStatus.textContent = "Please enter a simulated transcript."; }
  });
}

