import { useState, useRef, useEffect } from "react";
import { sendQuery, getSuggestedQuestions } from "@/lib/api";
import { Sparkles } from "lucide-react";

interface Message {
  role:    "user" | "assistant";
  text:    string;
  engine?: string;
}

interface Props {
  datasetId: string;
}

const QueryChat = ({ datasetId }: Props) => {
  const [messages,  setMessages]  = useState<Message[]>([]);
  const [input,     setInput]     = useState("");
  const [loading,   setLoading]   = useState(false);
  const [suggested, setSuggested] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!datasetId) return;
    getSuggestedQuestions(datasetId)
      .then((res) => setSuggested(res.data.questions || []))
      .catch(() => {});
  }, [datasetId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (query: string) => {
    if (!query.trim() || loading || !datasetId) return;
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setInput("");
    setLoading(true);
    try {
      const res = await sendQuery(datasetId, query);
      setMessages((prev) => [
        ...prev,
        {
          role:   "assistant",
          text:   res.data.query_result,
          engine: res.data.query_engine,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: err.response?.data?.detail || "Failed to get answer." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 pb-4">
        {messages.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Ask anything about your dataset.
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-foreground"
              }`}
            >
              {msg.text}
              {msg.engine && (
                <span className="ml-2 text-xs opacity-50">[{msg.engine}]</span>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-xl px-4 py-3 text-sm text-muted-foreground">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggested questions */}
      {messages.length === 0 && suggested.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {suggested.map((q) => (
            <button
              key={q}
              onClick={() => send(q)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border/50 bg-card text-xs hover:border-primary/30 hover:bg-primary/5 transition-all"
            >
              <Sparkles className="h-3 w-3 text-primary" />
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2 pt-3 border-t border-border/50">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send(input)}
          placeholder="Ask about your data..."
          disabled={loading || !datasetId}
          className="flex-1 px-4 py-2 rounded-lg border border-border/50 bg-background text-sm focus:outline-none focus:border-primary/50"
        />
        <button
          onClick={() => send(input)}
          disabled={loading || !input.trim() || !datasetId}
          className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default QueryChat;