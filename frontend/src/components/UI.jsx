import { useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import { Mic } from "lucide-react"; 

export const UI = ({ hidden, ...props }) => {
  const input = useRef();
  const { chat, loading, cameraZoomed, setCameraZoomed, message } = useChat();
  const [recording, setRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);

  const sendMessage = () => {
    const text = input.current.value.trim();
    if (!text) return;
    if (!loading && !message) {
      chat(text);
      input.current.value = "";
    }
  };

  const handleVoiceToggle = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Voice recognition not supported in this browser.");
      return;
    }

    // If already recording, stop it
    if (recording && recognition) {
      recognition.stop();
      setRecording(false);
      return;
    }

    // Otherwise, start a new recording
    const rec = new window.webkitSpeechRecognition();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.maxAlternatives = 1;

    rec.onstart = () => setRecording(true);
    rec.onend = () => setRecording(false);

    rec.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      input.current.value = transcript;
      sendMessage();
    };

    rec.start();
    setRecognition(rec);
  };

  if (hidden) return null;

  return (
    <>
      <div className="fixed inset-0 -z-10">
        <div className="background">
          {Array.from({ length: 20 }).map((_, i) => (
            <span key={i}></span>
          ))}
        </div>
      </div>

      <div className="fixed inset-0 z-10 flex flex-row">
        <div className="flex-[0.6] flex items-center justify-center relative">
          <div className="absolute top-4 right-7 space-x-2 flex">
            <button
              onClick={() => setCameraZoomed(!cameraZoomed)}
              className="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-md"
            >
              {cameraZoomed ? "Zoom Out" : "Zoom In"}
            </button>

            {/* Talk to Agent Button */}
            <button
              onClick={handleVoiceToggle}
              className={`${
                recording ? "bg-red-500 hover:bg-red-600" : "bg-purple-500 hover:bg-purple-600"
              } text-white px-4 py-2 rounded-md flex items-center space-x-2`}
            >
              <Mic className="w-5 h-5" />
              <span>{recording ? "Stop Talking" : "Talk to Agent"}</span>
            </button>
          </div>
        </div>

        <div className="flex-[0.4] p-[9px] rounded-3xl bg-white/20 shadow-2xl backdrop-blur-lg">
          <div className="flex flex-col bg-white/10 backdrop-blur-md rounded-3xl h-full shadow-inner shadow-gray-200 ring-1 ring-blue-300/30">
            <div className="flex-1 relative overflow-y-auto p-4 space-y-3 rounded-3xl">
              <div className="absolute top-0 left-0 w-full h-6 bg-gradient-to-b from-white/10 pointer-events-none"></div>
              <div className="absolute bottom-0 left-0 w-full h-6 bg-gradient-to-t from-white/10 pointer-events-none"></div>

              <div className="self-start max-w-xs px-5 py-4 rounded-2xl bg-gray-100
                              shadow-lg border border-gray-300 text-gray-900 text-lg font-semibold font-sans
                              hover:brightness-105 transition-all duration-150 animate-fadeIn">
                Hi! How are you feeling today?
              </div>

              {loading && (
                <div className="self-end max-w-xs px-5 py-4 rounded-2xl bg-gray-200
                                shadow-lg text-gray-800 font-medium text-lg flex items-center">
                  Thinking
                  <span className="ml-2 flex space-x-1">
                    <span className="w-1.5 h-1.5 bg-gray-800 rounded-full animate-bounce delay-75"></span>
                    <span className="w-1.5 h-1.5 bg-gray-800 rounded-full animate-bounce delay-150"></span>
                    <span className="w-1.5 h-1.5 bg-gray-800 rounded-full animate-bounce delay-300"></span>
                  </span>
                </div>
              )}

              {message && !loading && (
                <div className="self-end max-w-xs px-5 py-4 rounded-2xl bg-blue-500 text-white shadow-lg
                                text-lg font-medium">
                  {message.text}
                </div>
              )}
            </div>

            {/* Input Row with Voice Button */}
            <div className="flex flex-row border-t border-gray-300 rounded-b-2xl overflow-hidden">
              <input
                className="flex-1 placeholder:text-gray-800 placeholder:italic p-3 bg-white
                           focus:ring-2 focus:ring-blue-400 focus:outline-none transition-all duration-150"
                placeholder="Type a message..."
                ref={input}
                onKeyDown={(e) => { if (e.key === "Enter") sendMessage(); }}
              />

              {/* Mic toggle inside input row too */}
              <button
                onClick={handleVoiceToggle}
                className={`${
                  recording ? "bg-red-500 hover:bg-red-600" : "bg-purple-500 hover:bg-purple-600"
                } text-white px-4 flex items-center justify-center`}
              >
                <Mic className="w-5 h-5" />
              </button>

              <button
                disabled={loading || message}
                onClick={sendMessage}
                className={`bg-blue-500 hover:bg-blue-600 text-white px-6 font-semibold uppercase
                            transition-all duration-150 ${loading || message ? "cursor-not-allowed opacity-30" : ""}`}
              >
                Send
              </button>
            </div>

          </div>
        </div>
      </div>
    </>
  );
};
