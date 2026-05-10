import { useState, useRef } from "react";
import { Upload, FileSpreadsheet, X } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { uploadAndAnalyze, setSelectedDataset } from "@/lib/api";

const UploadPage = () => {
  const [file,      setFile]      = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragging,  setDragging]  = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const navigate    = useNavigate();
  const { toast }   = useToast();
  const { user }    = useAuth();

  // ── Drag events ─────────────────────────────────────────────────────────────
  const onDragOver  = (e: React.DragEvent) => { e.preventDefault(); setDragging(true);  };
  const onDragLeave = (e: React.DragEvent) => { e.preventDefault(); setDragging(false); };
  const onDrop      = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) validateAndSet(dropped);
  };

  const validateAndSet = (f: File) => {
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (!["csv", "xlsx", "xls"].includes(ext || "")) {
      toast({ title: "Invalid file", description: "Only CSV and Excel files are supported." });
      return;
    }
    setFile(f);
  };

  // ── Upload + analyze ─────────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!file)  return;
    if (!user)  {
      toast({ title: "Not authenticated", description: "Please login first" });
      return;
    }

    try {
      setUploading(true);

      const res     = await uploadAndAnalyze(file);
      const dataset = res.data;

      setSelectedDataset(dataset.dataset_id, dataset.file_name);

      toast({
        title:       "Upload successful",
        description: "Analysis started. Redirecting to insights...",
      });

      setFile(null);
      setTimeout(() => navigate(`/dashboard/insights/${dataset.dataset_id}`), 1500);

    } catch (err: any) {
      toast({
        title:       "Upload error",
        description: err.response?.data?.detail || "Something went wrong",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto py-16 space-y-6">

      {/* ── Page header ──────────────────────────────────────────────────────── */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Upload Dataset</h1>
        <p className="text-sm text-muted-foreground">
          Upload a CSV or Excel file to start AI-powered analysis.
        </p>
      </div>

      {/* ── Drop zone ────────────────────────────────────────────────────────── */}
      <div
        onClick={() => !file && inputRef.current?.click()}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`
          relative flex flex-col items-center justify-center gap-3
          rounded-2xl border-2 border-dashed p-12 transition-all cursor-pointer
          ${dragging
            ? "border-primary bg-primary/10 scale-[1.01]"
            : file
              ? "border-primary/50 bg-primary/5 cursor-default"
              : "border-border/50 bg-card hover:border-primary/30 hover:bg-primary/5"
          }
        `}
      >
        {/* Hidden native input */}
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) validateAndSet(f);
          }}
        />

        {file ? (
          /* ── File selected state ─────────────────────────────────────────── */
          <>
            <div className="h-14 w-14 rounded-xl bg-primary/10 flex items-center justify-center">
              <FileSpreadsheet className="h-7 w-7 text-primary" />
            </div>

            <div className="text-center space-y-1">
              <p className="text-sm font-medium truncate max-w-[260px]">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024).toFixed(1)} KB
                {" · "}
                {file.name.split(".").pop()?.toUpperCase()}
              </p>
            </div>

            {/* Remove file */}
            <button
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
              className="absolute top-3 right-3 h-7 w-7 rounded-full bg-muted flex items-center justify-center hover:bg-destructive/10 hover:text-destructive transition-colors"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </>
        ) : (
          /* ── Empty state ─────────────────────────────────────────────────── */
          <>
            <div className="h-14 w-14 rounded-xl bg-muted flex items-center justify-center">
              <Upload className="h-7 w-7 text-muted-foreground" />
            </div>
            <div className="text-center space-y-1">
              <p className="text-sm font-medium">
                Drop your file here, or{" "}
                <span className="text-primary underline underline-offset-2">browse</span>
              </p>
              <p className="text-xs text-muted-foreground">
                Supports CSV, XLSX, XLS · Max 50MB
              </p>
            </div>
          </>
        )}
      </div>

      {/* ── What happens next ────────────────────────────────────────────────── */}
      {!file && (
        <div className="grid grid-cols-3 gap-3 text-center">
          {[
            { step: "1", label: "Upload file"      },
            { step: "2", label: "AI analyzes data" },
            { step: "3", label: "View insights"    },
          ].map((item) => (
            <div key={item.step} className="p-3 rounded-xl border border-border/50 bg-card space-y-1">
              <div className="text-xs font-medium text-primary">Step {item.step}</div>
              <div className="text-xs text-muted-foreground">{item.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* ── Upload button ─────────────────────────────────────────────────────── */}
      <Button
        variant="hero"
        className="w-full"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? (
          <span className="flex items-center gap-2">
            <span className="h-4 w-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
            Uploading & analyzing...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Upload & Analyze
          </span>
        )}
      </Button>

      {/* ── Back link ────────────────────────────────────────────────────────── */}
      <div className="text-center">
        <Link to="/dashboard">
          <Button variant="ghost" size="sm">Back to Dashboard</Button>
        </Link>
      </div>

    </div>
  );
};

export default UploadPage;