import { useState } from "react";
import { Upload } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";

import FileUpload from "@/components/FileUpload";

import {
  uploadDataset,
  uploadAndAnalyze,
  setSelectedDataset
} from "@/lib/api";

const UploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();

  // ── OLD FLOW (manual upload) ───────────────────────────────────────────────
  const handleUpload = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please choose a CSV or Excel file"
      });
      return;
    }

    if (!user) {
      toast({
        title: "Not authenticated",
        description: "Please login first"
      });
      return;
    }

    try {
      setUploading(true);

      const res = await uploadDataset(file);
      const dataset = res.data;

      setSelectedDataset(dataset.id, dataset.file_name);

      toast({
        title: "Upload successful",
        description: "Redirecting to workspace..."
      });

      setFile(null);

      setTimeout(() => navigate("/dashboard/workspace"), 1200);

    } catch (err: any) {
      toast({
        title: "Upload error",
        description: err.response?.data?.detail || "Something went wrong"
      });
    } finally {
      setUploading(false);
    }
  };

  // ── NEW FLOW (auto upload + analysis) ──────────────────────────────────────
  const handleAutoUpload = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please choose a CSV or Excel file"
      });
      return;
    }

    try {
      setUploading(true);

      const res = await uploadAndAnalyze(file);
      const dataset = res.data;

      setSelectedDataset(dataset.dataset_id, dataset.file_name);

      toast({
        title: "Upload successful",
        description: "Analysis started. Redirecting..."
      });

      setFile(null);

      setTimeout(() => navigate(`/dashboard/insights/${dataset.dataset_id}`), 1500);

    } catch (err: any) {
      toast({
        title: "Upload error",
        description: err.response?.data?.detail || "Something went wrong"
      });
    } finally {
      setUploading(false);
    }
  };

  // ── FileUpload component callbacks ─────────────────────────────────────────
  const handleComplete = (datasetId: string) => {
    toast({
      title: "Upload successful",
      description: "Analysis started. Redirecting to insights..."
    });

    setSelectedDataset(datasetId);

    setTimeout(() => navigate(`/dashboard/insights/${datasetId}`), 1500);
  };

  const handleError = (msg: string) => {
    toast({
      title: "Upload error",
      description: msg
    });
  };

  return (
    <div className="text-center py-20 space-y-6">
      <Upload className="h-12 w-12 text-muted-foreground mx-auto" />

      <h2 className="text-xl font-semibold">Upload Dataset</h2>

      <p className="text-muted-foreground text-sm">
        Select a CSV or Excel file. You can upload manually or auto-analyze.
      </p>

      {/* ── NEW DRAG & DROP COMPONENT ── */}
      <div className="max-w-sm mx-auto">
        <FileUpload
          onUploadComplete={handleComplete}
          onError={handleError}
        />
      </div>

      {/* ── OLD FILE INPUT ── */}
      <input
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="mx-auto block"
      />

      {file && (
        <p className="text-xs text-muted-foreground">
          Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
        </p>
      )}

      {/* ── ACTION BUTTONS ── */}
      <div className="flex gap-3 justify-center">
        <Button onClick={handleUpload} disabled={uploading}>
          {uploading ? "Uploading..." : "Upload Only"}
        </Button>

        <Button variant="hero" onClick={handleAutoUpload} disabled={uploading}>
          {uploading ? "Processing..." : "Upload & Analyze"}
        </Button>
      </div>

      {/* ── BACK BUTTON ── */}
      <div>
        <Link to="/dashboard">
          <Button variant="ghost">Back to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
};

export default UploadPage;