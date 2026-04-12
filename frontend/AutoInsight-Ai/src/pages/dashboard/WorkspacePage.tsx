import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { FileSpreadsheet, Play, Eye, Upload, MessageSquare } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { Link, useNavigate } from "react-router-dom";
import {
  listDatasets,
  startAnalysis,
  deleteDataset,
  renameDataset,
  setSelectedDataset,
} from "@/lib/api";

interface Dataset {
  id: string;
  file_name: string;
  file_size: string;
  row_count?: string;
  column_count?: string;
  created_at: string;
}

const WorkspacePage = () => {
  const [datasets, setDatasets]   = useState<Dataset[]>([]);
  const [selected, setSelected]   = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading]     = useState(true);

  const { toast }    = useToast();
  const { user }     = useAuth();
  const navigate     = useNavigate();

  // ── Load datasets ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (!user) return;
    listDatasets()
      .then((res) => setDatasets(res.data || []))
      .catch(() =>
        toast({ title: "Error", description: "Failed to load datasets" })
      )
      .finally(() => setLoading(false));
  }, [user]);

  // ── Start analysis for selected dataset ───────────────────────────────────
  const handleStartAnalysis = async () => {
    const ds = datasets[selected];
    if (!ds) return;

    try {
      setAnalyzing(true);

      // Store selected dataset globally
      setSelectedDataset(ds.id, ds.file_name);

      await startAnalysis(ds.id);

      toast({
        title: "Analysis Started",
        description: "AI pipeline is running. Redirecting to insights...",
      });

      // Navigate to insights page for this dataset
      setTimeout(() => navigate(`/dashboard/insights/${ds.id}`), 1500);

    } catch (err: any) {
      toast({
        title: "Error",
        description: err.response?.data?.detail || "Analysis failed",
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // ── Chat with AI for selected dataset ────────────────────────────────────
  const handleChatWithAI = (ds: Dataset) => {
    setSelectedDataset(ds.id, ds.file_name);
    navigate("/dashboard/chat");
  };

  // ── Select dataset ────────────────────────────────────────────────────────
  const handleSelect = (index: number, ds: Dataset) => {
    setSelected(index);
    setSelectedDataset(ds.id, ds.file_name);
  };

  // ── Loading state ─────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (datasets.length === 0) {
    return (
      <div className="text-center py-20 space-y-4">
        <Upload className="h-12 w-12 text-muted-foreground mx-auto" />
        <h2 className="text-xl font-semibold">No datasets yet</h2>
        <p className="text-muted-foreground text-sm">
          Upload a dataset to get started.
        </p>
        <Button variant="hero" asChild>
          <Link to="/dashboard/upload">Upload Dataset</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-1">Workspace</h1>
          <p className="text-sm text-muted-foreground">
            Select a dataset and start your AI analysis.
          </p>
        </div>

        <Button variant="hero" onClick={handleStartAnalysis} disabled={analyzing}>
          {analyzing ? (
            <>
              <div className="h-4 w-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Play className="h-4 w-4" /> Start Analysis
            </>
          )}
        </Button>
      </div>

      <div className="grid gap-3">
        {datasets.map((ds, i) => (
          <div
            key={ds.id}
            className={`flex items-center gap-4 p-4 rounded-xl border text-left transition-all ${
              selected === i
                ? "border-primary/50 bg-primary/5"
                : "border-border/50 bg-card hover:border-primary/20"
            }`}
          >
            {/* Clicking the row selects the dataset */}
            <button
              className="flex items-center gap-4 flex-1 min-w-0"
              onClick={() => handleSelect(i, ds)}
            >
              <FileSpreadsheet className="h-8 w-8 text-primary flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm">{ds.file_name}</div>
                <div className="text-xs text-muted-foreground">
                  {ds.file_size} ·{" "}
                  {ds.row_count ? `${ds.row_count} rows · ` : ""}
                  {new Date(ds.created_at).toLocaleDateString()}
                </div>
              </div>
            </button>

            {/* Chat with AI button per dataset */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleChatWithAI(ds)}
              className="flex-shrink-0 gap-1"
            >
              <MessageSquare className="h-4 w-4" />
              Chat
            </Button>

            <Eye className="h-4 w-4 text-muted-foreground flex-shrink-0" />
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkspacePage;