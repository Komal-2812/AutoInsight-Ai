import { useState, useEffect } from "react";
import { FileSpreadsheet } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { getHistory } from "@/lib/api";

interface HistoryItem {
  id?: string;
  type: string;
  dataset_id: string;
  dataset_name?: string;
  query?: string;
  user_id: string;
  status?: string;
  timestamp: string;
}

const HistoryPage = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) return;

    const loadHistory = async () => {
      try {
        const res = await getHistory();
        setHistory(res.data);
      } catch {
        toast({
          title: "Error",
          description: "Failed to load history",
        });
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, [user]);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">History</h1>

      {history.length === 0 ? (
        <p className="text-muted-foreground text-sm">No history found.</p>
      ) : (
        <div className="grid gap-3">
          {history.map((item, index) => (
            <div
              key={index}
              className="flex items-center gap-4 p-4 rounded-xl border"
            >
              <FileSpreadsheet className="h-6 w-6 text-primary" />

              <div className="flex-1">
                <div className="text-sm font-medium">
                  {item.dataset_name || item.dataset_id}
                </div>
                <div className="text-xs text-muted-foreground">
                  {item.type === "chat" && item.query
                    ? `Chat: ${item.query.slice(0, 60)}${item.query.length > 60 ? "..." : ""} · `
                    : ""}
                  {item.status ? `${item.status} · ` : ""}
                  {item.type} ·{" "}
                  {new Date(item.timestamp).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HistoryPage;