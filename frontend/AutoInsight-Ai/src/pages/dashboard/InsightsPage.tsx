import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import {
  TrendingUp, TrendingDown, DollarSign, Users,
  ShoppingCart, Target, RefreshCw,
} from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getAnalysis, pollAnalysis, getSelectedDatasetId } from "@/lib/api";

const KPI_ICONS  = [DollarSign, Users, Target, ShoppingCart];
const COLORS     = [
  "hsl(174, 72%, 50%)",
  "hsl(199, 89%, 48%)",
  "hsl(220, 70%, 50%)",
  "hsl(280, 65%, 60%)",
];

const InsightsPage = () => {
  // Support both /insights/:datasetId and /insights (uses localStorage)
  const { datasetId: paramId } = useParams<{ datasetId?: string }>();
  const navigate = useNavigate();

  const datasetId = paramId || getSelectedDatasetId() || "";

  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading]   = useState(true);
  const [polling, setPolling]   = useState(false);
  const [status, setStatus]     = useState("");
  const [error, setError]       = useState("");

  const [barData,  setBarData]  = useState<any[]>([]);
  const [lineData, setLineData] = useState<any[]>([]);
  const [pieData,  setPieData]  = useState<any[]>([]);
  const [kpis,     setKpis]     = useState<any[]>([]);
  const [insights, setInsights] = useState<string[]>([]);

  useEffect(() => {
    if (!datasetId) {
      setError("No dataset selected. Go to Workspace and select a dataset.");
      setLoading(false);
      return;
    }

    getAnalysis(datasetId)
      .then((res) => {
        const s = res.data.status;
        if (s === "completed") {
          applyAnalysis(res.data);
          setLoading(false);
        } else if (s === "running" || s === "pending") {
          setPolling(true);
          setLoading(false);
          startPolling();
        } else {
          setLoading(false);
        }
      })
      .catch(() => {
        setPolling(true);
        setLoading(false);
        startPolling();
      });
  }, [datasetId]);

  const startPolling = () => {
    pollAnalysis(
      datasetId,
      (s) => setStatus(s),
      (data) => {
        applyAnalysis(data);
        setPolling(false);
      },
      () => {
        setError("Analysis failed. Please try again from Workspace.");
        setPolling(false);
      }
    );
  };

  const applyAnalysis = (data: any) => {
    setAnalysis(data);

    // KPIs
    if (data.kpis?.length) {
      setKpis(
        data.kpis.map((kpi: any, i: number) => ({
          label:  kpi.label,
          value:  kpi.unit ? `${kpi.value} ${kpi.unit}` : String(kpi.value),
          change: kpi.trend === "up" ? "+↑" : kpi.trend === "down" ? "-↓" : "→",
          up:     kpi.trend !== "down",
          icon:   KPI_ICONS[i % KPI_ICONS.length],
        }))
      );
    }

    // Insights
    if (data.insights?.length) setInsights(data.insights);

    // Charts
    if (data.charts?.length) {
      data.charts.forEach((chart: any) => {
        const plotly = chart.plotly_json;
        if (!plotly?.data?.length) return;
        const type  = chart.type;
        const trace = plotly.data[0];

        if (type === "bar" || type === "histogram") {
          const xs: any[] = trace.x || [];
          const ys: any[] = trace.y || [];
          setBarData(
            xs.map((x: any, i: number) => ({
              name: String(x),
              [trace.name || "value"]: ys[i] ?? 0,
              ...(plotly.data[1]
                ? { [plotly.data[1].name || "value2"]: (plotly.data[1].y || [])[i] ?? 0 }
                : {}),
            }))
          );
        }

        if (type === "line" || type === "scatter") {
          const xs: any[] = trace.x || [];
          setLineData(
            xs.map((x: any, i: number) => {
              const point: any = { name: String(x) };
              plotly.data.forEach((t: any) => {
                point[t.name || "value"] = (t.y || [])[i] ?? 0;
              });
              return point;
            })
          );
        }

        if (type === "pie") {
          const labels: any[] = trace.labels || [];
          const values: any[] = trace.values || [];
          setPieData(
            labels.map((label: any, i: number) => ({
              name:  String(label),
              value: values[i] ?? 0,
            }))
          );
        }
      });
    }

    // Fallback: use table data for bar chart if no charts
    if (!data.charts?.length && data.tables?.length) {
      const table = data.tables[0];
      if (table.headers?.length >= 2 && table.rows?.length) {
        setBarData(
          table.rows.slice(0, 10).map((row: any[]) => ({
            name:  String(row[0]),
            value: Number(row[1]) || 0,
          }))
        );
      }
    }
  };

  const barKeys  = barData.length  ? Object.keys(barData[0]).filter(k => k !== "name")  : ["value"];
  const lineKeys = lineData.length ? Object.keys(lineData[0]).filter(k => k !== "name") : ["value"];

  // Loading
  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold mb-1">Insights Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            AI-generated insights from your latest analysis.
          </p>
        </div>
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <RefreshCw className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground text-sm">Loading analysis…</p>
        </div>
      </div>
    );
  }

  // Polling
  if (polling) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold mb-1">Insights Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            AI-generated insights from your latest analysis.
          </p>
        </div>
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <RefreshCw className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground text-sm">
            AI pipeline is running… this takes 15–60 seconds
          </p>
          {status && (
            <p className="text-xs text-muted-foreground">Status: {status}</p>
          )}
        </div>
      </div>
    );
  }

  // Error
  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold mb-1">Insights Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            AI-generated insights from your latest analysis.
          </p>
        </div>
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <p className="text-destructive text-sm">{error}</p>
          <button
            onClick={() => navigate("/dashboard/workspace")}
            className="text-primary text-sm underline"
          >
            Go to Workspace
          </button>
        </div>
      </div>
    );
  }

  const finalBarData  = barData.length  ? barData  : [{ name: "No data", value: 0 }];
  const finalLineData = lineData.length ? lineData : [{ name: "No data", value: 0 }];
  const finalPieData  = pieData.length  ? pieData  : [{ name: "No data", value: 1 }];
  const finalKpis     = kpis.length     ? kpis     : [];
  const finalInsights = insights.length ? insights : ["No insights generated yet."];
  const finalBarKeys  = barKeys.length  ? barKeys  : ["value"];
  const finalLineKeys = lineKeys.length ? lineKeys : ["value"];

  const barChartTitle  = analysis?.charts?.find((c: any) => c.type === "bar" || c.type === "histogram")?.title || "Data Overview";
  const lineChartTitle = analysis?.charts?.find((c: any) => c.type === "line" || c.type === "scatter")?.title  || "Trend Analysis";
  const pieChartTitle  = analysis?.charts?.find((c: any) => c.type === "pie")?.title || "Distribution";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-1">Insights Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          AI-generated insights from your latest analysis.
        </p>
      </div>

      {/* KPIs */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {finalKpis.map((kpi, i) => (
          <motion.div
            key={kpi.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="p-5 rounded-xl border border-border/50 bg-card"
          >
            <div className="flex items-center justify-between mb-2">
              <kpi.icon className="h-5 w-5 text-primary" />
              <span className={`text-xs font-medium flex items-center gap-0.5 ${kpi.up ? "text-primary" : "text-destructive"}`}>
                {kpi.up
                  ? <TrendingUp className="h-3 w-3" />
                  : <TrendingDown className="h-3 w-3" />}
                {kpi.change}
              </span>
            </div>
            <div className="text-2xl font-bold">{kpi.value}</div>
            <div className="text-xs text-muted-foreground">{kpi.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl border border-border/50 bg-card">
          <h3 className="font-semibold mb-4">{barChartTitle}</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={finalBarData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px" }} />
              {finalBarKeys.map((key, i) => (
                <Bar key={key} dataKey={key} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="p-6 rounded-xl border border-border/50 bg-card">
          <h3 className="font-semibold mb-4">{lineChartTitle}</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={finalLineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
              <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px" }} />
              {finalLineKeys.map((key, i) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={COLORS[i % COLORS.length]}
                  strokeWidth={2}
                  dot={{ fill: COLORS[i % COLORS.length] }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pie + AI Insights */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl border border-border/50 bg-card">
          <h3 className="font-semibold mb-4">{pieChartTitle}</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={finalPieData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {finalPieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="p-6 rounded-xl border border-border/50 bg-card">
          <h3 className="font-semibold mb-4">🧠 AI Insights</h3>
          <div className="space-y-3">
            {finalInsights.map((insight, i) => (
              <div key={i} className="flex gap-2 p-3 rounded-lg bg-muted/30 text-sm">
                <span className="text-primary font-bold mt-0.5">{i + 1}.</span>
                <span className="text-muted-foreground">{insight}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InsightsPage;