import { BarChart3, Upload, MessageSquare, TrendingUp, FileSpreadsheet } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { useEffect, useState } from "react";
import { listDatasets, setSelectedDataset } from "@/lib/api";

interface Dataset {
  id: string;
  file_name: string;
  status?: string;
  created_at: string;
}

const DashboardHome = () => {
  const { user } = useAuth();
  const [datasetCount, setDatasetCount] = useState(0);
  const [datasets, setDatasets] = useState<Dataset[]>([]);

  useEffect(() => {
    if (!user) return;
    listDatasets()
      .then((res) => {
        const data = res.data || [];
        setDatasets(data.slice(0, 5));
        setDatasetCount(data.length);
      })
      .catch(() => console.error("Failed to load datasets"));
  }, [user]);

  const stats = [
    {
      label: "Datasets",
      value: String(datasetCount),
      icon: FileSpreadsheet,
      change: "total",
    },
    {
      label: "Analyses",
      value: String(datasetCount),
      icon: BarChart3,
      change: "completed",
    },
    {
      label: "Insights",
      value: datasetCount > 0 ? "Ready" : "—",
      icon: TrendingUp,
      change: "available",
    },
    {
      label: "AI Chats",
      value: "∞",
      icon: MessageSquare,
      change: "unlimited",
    },
  ];

  return (
    <div className="space-y-8">
      {/* HEADER */}
      <div>
        <h1 className="text-2xl font-bold mb-1">
          Welcome back{user?.full_name ? `, ${user.full_name}` : ""}
        </h1>
        <p className="text-muted-foreground text-sm">
          Here's an overview of your data analysis activity.
        </p>
      </div>

      {/* STATS */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="p-5 rounded-xl border border-border/50 bg-card"
          >
            <div className="flex items-center justify-between mb-3">
              <stat.icon className="h-5 w-5 text-primary" />
              <span className="text-xs text-primary font-medium">
                {stat.change}
              </span>
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-xs text-muted-foreground">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* ACTIONS + RECENT */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* QUICK ACTIONS */}
        <div className="p-6 rounded-xl border border-border/50 bg-card">
          <h2 className="font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: "Upload Dataset", to: "/dashboard/upload", icon: Upload },
              { label: "Chat with AI",   to: "/dashboard/chat",   icon: MessageSquare },
              { label: "View Insights",  to: "/dashboard/insights", icon: BarChart3 },
              { label: "Workspace",      to: "/dashboard/workspace", icon: FileSpreadsheet },
            ].map((action) => (
              <Link
                key={action.label}
                to={action.to}
                className="flex items-center gap-3 p-3 rounded-lg border border-border/50 hover:border-primary/30 hover:bg-primary/5 transition-all text-sm"
              >
                <action.icon className="h-4 w-4 text-primary" />
                {action.label}
              </Link>
            ))}
          </div>
        </div>

        {/* RECENT DATASETS */}
        <div className="p-6 rounded-xl border border-border/50 bg-card">
          <h2 className="font-semibold mb-4">Recent Datasets</h2>
          {datasets.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No datasets yet. Upload one to get started!
            </p>
          ) : (
            <div className="space-y-4">
              {datasets.map((ds) => (
                <div
                  key={ds.id}
                  className="flex items-center gap-3 cursor-pointer"
                  onClick={() => setSelectedDataset(ds.id, ds.file_name)}
                >
                  <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <FileSpreadsheet className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm truncate font-medium">
                      {ds.file_name}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(ds.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;