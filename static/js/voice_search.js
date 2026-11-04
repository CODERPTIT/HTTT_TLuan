const voiceOpen = document.getElementById("voice-open");
const voiceDialog = document.getElementById("voice-dialog");
voiceOpen?.addEventListener("click", () => voiceDialog.showModal());

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

async function transcribeAudio(file, input, status, button) {
  status.textContent = "Transcribing your recording…";
  button.disabled = true;
  const form = new FormData();
  form.append("audio", file);
  try {
    const response = await fetch("/search/transcribe", {
      method: "POST", body: form, headers: {Accept: "application/json"}
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Transcription failed.");
    input.value = result.transcript;
    input.dispatchEvent(new Event("input", {bubbles: true}));
    status.textContent = "Transcript ready. Review it before searching.";
  } catch (error) {
    status.textContent = `${error.message} You can type your search instead.`;
  } finally {
    button.disabled = false;
  }
}

function setupVoiceInput(button, input, status, idleLabel) {
  if (!button || !input || !status) return;
  const label = button.querySelector(".record-label");
  let recorder;
  let recordingStream;
  let recordingTimer;

  const setButtonState = (text, recording = false) => {
    label.textContent = text;
    button.classList.toggle("recording", recording);
    button.setAttribute("aria-pressed", String(recording));
  };

  button.addEventListener("click", async () => {
    if (recorder?.state === "recording") {
      recorder.stop();
      clearTimeout(recordingTimer);
      button.disabled = true;
      return;
    }

    if (window.MediaRecorder && MediaRecorder.isTypeSupported("audio/webm") && navigator.mediaDevices?.getUserMedia) {
      try {
        recordingStream = await navigator.mediaDevices.getUserMedia({audio: true});
        recorder = new MediaRecorder(recordingStream, {mimeType: "audio/webm"});
        const chunks = [];
        recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
        recorder.onstop = () => {
          recordingStream.getTracks().forEach(track => track.stop());
          setButtonState(idleLabel);
          if (chunks.length) {
            const mime = recorder.mimeType.split(";", 1)[0] || "audio/webm";
            transcribeAudio(new File(chunks, "recording.webm", {type: mime}), input, status, button);
          } else {
            button.disabled = false;
            status.textContent = "No audio was recorded. Try again or type your search.";
          }
        };
        recorder.start();
        setButtonState("Stop", true);
        status.textContent = "Recording… Speak your product description or filters, then stop.";
        recordingTimer = setTimeout(() => {
          if (recorder.state === "recording") recorder.stop();
        }, 30000);
      } catch {
        status.textContent = "Microphone access failed. Allow it in your browser or type your search.";
      }
      return;
    }

    if (!SpeechRecognition) {
      status.textContent = "Microphone recognition is unavailable in this browser. Type your search instead.";
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = navigator.language || "vi-VN";
    recognition.onstart = () => {
      button.disabled = true;
      status.textContent = "Listening…";
    };
    recognition.onresult = event => {
      input.value = event.results[0][0].transcript;
      input.dispatchEvent(new Event("input", {bubbles: true}));
      status.textContent = "Transcript ready. Review it before searching.";
    };
    recognition.onerror = event => {
      status.textContent = `Microphone recognition failed (${event.error}). Type your search instead.`;
    };
    recognition.onend = () => { button.disabled = false; };
    recognition.start();
  });
}

const voiceRecord = document.getElementById("voice-record");
const voiceStatus = document.getElementById("voice-status");
const transcriptInput = document.getElementById("transcript");
const audioInput = document.getElementById("audio-input");
setupVoiceInput(voiceRecord, transcriptInput, voiceStatus, "Start recording");

audioInput?.addEventListener("change", () => {
  const file = audioInput.files[0];
  if (!file) return;
  if (file.size > 10 * 1024 * 1024) {
    voiceStatus.textContent = "Choose a recording up to 10 MB.";
    audioInput.value = "";
    return;
  }
  transcribeAudio(file, transcriptInput, voiceStatus, voiceRecord);
});

setupVoiceInput(
  document.getElementById("image-voice-record"),
  document.getElementById("image-query"),
  document.getElementById("image-voice-status"),
  "Voice"
);
