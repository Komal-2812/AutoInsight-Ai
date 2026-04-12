import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot, User, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { useToast } from "@/hooks/use-toast";
import ReactMarkdown from "react-markdown";

import {
  sendQuery, // NEW (LangGraph)
  chatWithAI, // OLD fallback
  getSelectedDatasetId,
  getSelectedDatasetName,
  getSuggestedQuestions
} from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  engine?: string;
  charts?: any[];
  tables?: any[];
  kpis?: any[];
}

const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI data analyst. Upload a dataset and ask me anything about your data.",
    },
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [datasetId, setDatasetId] = useState("");
  const [datasetName, setDatasetName] = useState("");
  const [suggested, setSuggested] = useState<string[]>([
    "What are the top 5 products by revenue?",
    "Show me the growth trend over time",
    "Which region is underperforming?",
    "Summarize the key patterns in this dataset",
  ]);

  const bottomRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // ── Auto scroll ─────────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Load dataset + suggestions ──────────────────────────────
  useEffect(() => {
    const id = getSelectedDatasetId() || "";
    const name = getSelectedDatasetName() || "";

    setDatasetId(id);
    setDatasetName(name);

    if (id) {
      getSuggestedQuestions(id)
        .then((res) => {
          if (res.data?.questions?.length) {
            setSuggested(res.data.questions);
          }
        })
        .catch(() => {});
    }
  }, []);

  // ── Send Message (LangGraph + fallback) ─────────────────────
  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    if (!datasetId) {
      toast({
        title: "No dataset selected",
        description: "Go to Workspace and select a dataset first.",
        variant: "destructive",
      });
      return;
    }

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      let data: any = null;

      // ── PRIMARY: LangGraph Query ─────────────────────
      try {
        const res = await sendQuery(datasetId, text);
        data = res.data;
      } catch {
        // ── FALLBACK: Old Chat API ─────────────────────
        const res = await chatWithAI(datasetId, text);
        data = res.data;
      }

      let content =
        data.query_result ||
        data.answer ||
        "I couldn't find an answer in the dataset.";

      // ── KPIs ────────────────────────────────────────
      if (data.kpis?.length) {
        const kpiLines = data.kpis
          .map(
            (k: any) =>
              `**${k.label || k.title}:** ${k.value}${k.unit ? " " + k.unit : ""}`
          )
          .join("\n");

        content += `\n\n**Key Metrics:**\n${kpiLines}`;
      }

      // ── Tables ──────────────────────────────────────
      if (data.tables?.length) {
        data.tables.forEach((table: any) => {
          if (!table.headers || !table.rows) return;

          content += `\n\n**${table.title || "Table"}**\n`;
          content += `| ${table.headers.join(" | ")} |\n`;
          content += `| ${table.headers.map(() => "---").join(" | ")} |\n`;

          table.rows.slice(0, 10).forEach((row: any[]) => {
            content += `| ${row.map(String).join(" | ")} |\n`;
          });
        });
      }

      const assistantMsg: Message = {
        role: "assistant",
        content,
        engine: data.query_engine, // NEW
        charts: data.charts || [],
        tables: data.tables || [],
        kpis: data.kpis || [],
      };

      setMessages((prev) => [...prev, assistantMsg]);

    } catch (err: any) {
      toast({
        title: "AI Error",
        description:
          err.response?.data?.detail || "Failed to connect to AI.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // ───────────────── UI (UNCHANGED) ──────────────────────────
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-1">Chat with AI</h1>
        <p className="text-sm text-muted-foreground">
          Ask questions about your data in natural language.
        </p>

        {datasetId ? (
          <p className="text-xs text-primary mt-1">
            ✓ Dataset active{datasetName ? `: ${datasetName}` : ""}
          </p>
        ) : (
          <p className="text-xs text-destructive mt-1">
            No dataset selected — go to Workspace first.
          </p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex gap-3 ${
              msg.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                msg.role === "assistant"
                  ? "gradient-bg"
                  : "bg-secondary"
              }`}
            >
              {msg.role === "assistant" ? (
                <Bot className="h-4 w-4 text-primary-foreground" />
              ) : (
                <User className="h-4 w-4 text-secondary-foreground" />
              )}
            </div>

            <div
              className={`max-w-[70%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "assistant"
                  ? "bg-card border border-border/50"
                  : "gradient-bg text-primary-foreground"
              }`}
            >
              {msg.role === "assistant" ? (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                  {msg.engine && (
                    <span className="text-xs opacity-40 ml-1">
                      [{msg.engine}]
                    </span>
                  )}
                </div>
              ) : (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              )}
            </div>
          </motion.div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-lg gradient-bg flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="bg-card border border-border/50 rounded-xl px-4 py-3">
              <div className="flex gap-1">
                {[0, 150, 300].map((d) => (
                  <div
                    key={d}
                    className="h-2 w-2 rounded-full bg-primary animate-bounce"
                    style={{ animationDelay: `${d}ms` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {suggested.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border/50 bg-card text-xs hover:border-primary/30 hover:bg-primary/5 transition-all"
            >
              <Sparkles className="h-3 w-3 text-primary" />
              {q}
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) =>
            e.key === "Enter" && !e.shiftKey && sendMessage(input)
          }
          placeholder="Ask about your data..."
          className="flex-1"
        />
        <Button
          variant="hero"
          size="icon"
          onClick={() => sendMessage(input)}
          disabled={isLoading || !input.trim()}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default ChatPage;