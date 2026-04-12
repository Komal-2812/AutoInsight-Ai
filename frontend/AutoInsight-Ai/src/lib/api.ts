import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000"
});

// ── Attach JWT Token ─────────────────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Dataset Selection ─────────────────────────────────────────────────────────
export const setSelectedDataset = (id: string, name?: string) => {
  localStorage.setItem("selected_dataset_id", id);
  if (name) localStorage.setItem("selected_dataset_name", name);
};

export const getSelectedDatasetId = (): string | null =>
  localStorage.getItem("selected_dataset_id");

export const getSelectedDatasetName = (): string | null =>
  localStorage.getItem("selected_dataset_name");

export const clearSelectedDataset = () => {
  localStorage.removeItem("selected_dataset_id");
  localStorage.removeItem("selected_dataset_name");
};

// ── Auth ─────────────────────────────────────────────────────────────────────
export const signup = (email: string, password: string, full_name?: string) =>
  api.post("/auth/signup", { email, password, full_name });

export const login = async (email: string, password: string) => {
  const res = await api.post("/auth/login", { email, password });
  localStorage.setItem("token", res.data.access_token);
  return res.data;
};

export const getProfile = () => api.get("/auth/profile");

export const logout = () => {
  localStorage.removeItem("token");
  clearSelectedDataset();
};

// ── Dataset ──────────────────────────────────────────────────────────────────
export const uploadDataset = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/dataset/upload", form);
};

// ✅ NEW: upload + auto analysis
export const uploadAndAnalyze = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/analysis/upload", form);
};

export const listDatasets = () => api.get("/dataset/list");
export const getDataset = (id: string) => api.get(`/dataset/${id}`);
export const getDatasetSummary = (id: string) => api.get(`/dataset/${id}/summary`);
export const deleteDataset = (id: string) => api.delete(`/dataset/${id}`);
export const renameDataset = (id: string, file_name: string) =>
  api.put(`/dataset/${id}/rename`, { file_name });

// ── Analysis ─────────────────────────────────────────────────────────────────
export const startAnalysis = (datasetId: string) =>
  api.post(`/analysis/start/${datasetId}`);

export const getAnalysis = (datasetId: string) =>
  api.get(`/analysis/${datasetId}`);

export const getAnalysisStatus = (datasetId: string) =>
  api.get(`/analysis/status/${datasetId}`);

// Polling helper (unchanged)
export const pollAnalysis = (
  datasetId: string,
  onUpdate: (status: string) => void,
  onComplete: (data: any) => void,
  onError?: (err: any) => void
): ReturnType<typeof setInterval> => {
  const interval = setInterval(async () => {
    try {
      const res = await getAnalysis(datasetId);
      const status = res.data.status;

      onUpdate(status);

      if (status === "completed" || status === "failed") {
        clearInterval(interval);
        onComplete(res.data);
      }
    } catch (err) {
      clearInterval(interval);
      onError?.(err);
    }
  }, 5000);

  return interval;
};

// ── Query (LangGraph system) ─────────────────────────────────────────────────
export const sendQuery = (dataset_id: string, query: string) =>
  api.post("/query", { dataset_id, query });

// ── Chat ─────────────────────────────────────────────────────────────────────
export const chatWithAI = (dataset_id: string, query: string) =>
  api.post("/chat", { dataset_id, query });

export const getSuggestedQuestions = (dataset_id: string) =>
  api.get(`/chat/suggested/${dataset_id}`);

// ── History ──────────────────────────────────────────────────────────────────
export const getHistory = () => api.get("/history");

// ── Dashboard (NEW) ──────────────────────────────────────────────────────────
export const getDashboardStats = () => api.get("/dashboard/stats");

// ── Downloads ────────────────────────────────────────────────────────────────
const downloadFile = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

export const downloadReport = (datasetId: string) =>
  api
    .get(`/download/report/${datasetId}`, { responseType: "blob" })
    .then((res) => downloadFile(res.data, `report_${datasetId}.pdf`));

export const downloadData = (datasetId: string) =>
  api
    .get(`/download/data/${datasetId}`, { responseType: "blob" })
    .then((res) => downloadFile(res.data, `data_${datasetId}.csv`));

export const downloadChart = (datasetId: string, chartIndex: number) =>
  api
    .get(`/download/chart/${datasetId}/${chartIndex}`, { responseType: "blob" })
    .then((res) => downloadFile(res.data, `chart_${chartIndex}.png`));

export default api;