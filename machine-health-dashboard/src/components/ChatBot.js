import React, { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send } from "lucide-react";
import { chatWithBot } from "../utils/api";

export default function ChatBot({
  latest,
  prediction,
  history
}) {
  const [open, setOpen] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi 👋 I'm your Machine Health Assistant. Ask me anything about the machine.",
    },
  ]);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const question = input;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: question,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const result = await chatWithBot(
        question,
        latest,
        prediction,
        history
      );

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Unable to contact AI assistant.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <>
      {/* Floating Button */}

      <button
        onClick={() => setOpen(!open)}
        className="
          fixed
          bottom-6
          right-6
          z-50
          w-14
          h-14
          rounded-full
          bg-cyan-500
          text-black
          shadow-lg
          flex
          items-center
          justify-center
        "
      >
        {open ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chat Window */}

      {open && (
        <div
          className="
            fixed
            bottom-24
            right-6
            z-50
            w-[380px]
            h-[600px]
            bg-[#0f172a]
            border
            border-cyan-500
            rounded-xl
            flex
            flex-col
            shadow-2xl
          "
        >
          {/* Header */}

          <div className="p-3 border-b border-slate-700">
            <h2 className="font-bold text-cyan-400">
              Machine Health Copilot
            </h2>
          </div>

          {/* Messages */}

          <div className="flex-1 overflow-y-auto p-3">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-3 ${
                  msg.role === "user"
                    ? "text-right"
                    : "text-left"
                }`}
              >
                <div
                  className={`inline-block p-3 rounded-lg max-w-[90%] whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-cyan-500 text-black"
                      : "bg-slate-800 text-white"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="text-slate-400 text-sm">
                Thinking...
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}

          <div className="p-3 border-t border-slate-700 flex gap-2">
            <input
              className="
                flex-1
                bg-slate-800
                text-white
                rounded
                px-3
                py-2
              "
              placeholder="Ask about machine health..."
              value={input}
              onChange={(e) =>
                setInput(e.target.value)
              }
              onKeyDown={(e) =>
                e.key === "Enter" &&
                sendMessage()
              }
            />

            <button
              onClick={sendMessage}
              className="
                px-3
                bg-cyan-500
                text-black
                rounded
              "
            >
              <Send size={18} />
            </button>
          </div>

          {/* Suggestions */}

          <div className="p-2 border-t border-slate-700 text-xs text-slate-400">
            Try:
            <br />
            • What is the current status?
            <br />
            • Why is risk increasing?
            <br />
            • What does this machine do?
          </div>
        </div>
      )}
    </>
  );
}