import { useState } from "react";
import { uploadAndAnalyze, setSelectedDataset } from "@/lib/api";

interface Props {
  onUploadComplete: (datasetId: string) => void;
  onError:          (msg: string) => void;
}

const FileUpload = ({ onUploadComplete, onError }: Props) => {
  const [file,      setFile]      = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress,  setProgress]  = useState("");

  const handleUpload = async () => {
    if (!file) return;
    try {
      setUploading(true);
      setProgress("Uploading file...");
      const res                     = await uploadAndAnalyze(file);
      const { dataset_id, file_name } = res.data;
      setSelectedDataset(dataset_id, file_name);
      setProgress("Analysis started...");
      onUploadComplete(dataset_id);
    } catch (err: any) {
      onError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      setProgress("");
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <input
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        disabled={uploading}
        className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
      />
      {file && (
        <p className="text-xs text-muted-foreground">
          {file.name} ({(file.size / 1024).toFixed(1)} KB)
        </p>
      )}
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium disabled:opacity-50"
      >
        {uploading ? "Uploading..." : "Upload & Analyze"}
      </button>
      {progress && (
        <p className="text-xs text-muted-foreground">{progress}</p>
      )}
    </div>
  );
};

export default FileUpload;