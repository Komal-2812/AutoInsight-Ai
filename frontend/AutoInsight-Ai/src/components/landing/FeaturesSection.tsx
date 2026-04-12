import { Brain, BarChart3, Zap, MessageSquare, Shield, Layers } from "lucide-react";
import { motion } from "framer-motion";

const features = [
  {
    icon: Brain,
    title: "AI Multi-Agent System",
    description: "10+ specialized agents work together to clean, analyze, and generate insights from your data automatically.",
  },
  {
    icon: BarChart3,
    title: "Auto Dashboard Builder",
    description: "Instantly generate interactive dashboards with charts, KPIs, and filters — no configuration needed.",
  },
  {
    icon: Zap,
    title: "Smart Insights",
    description: "Get AI-generated recommendations, patterns, and anomalies surfaced from your datasets in seconds.",
  },
  {
    icon: MessageSquare,
    title: "Chat with Your Data",
    description: "Ask questions in natural language and receive context-aware answers powered by your dataset.",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "Data isolation, encryption, and role-based access ensure your data stays private and protected.",
  },
  {
    icon: Layers,
    title: "Workspace Management",
    description: "Organize datasets, analyses, and dashboards in a clean workspace with full history tracking.",
  },
];

const FeaturesSection = () => {
  return (
    <section id="features" className="py-24 relative">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Everything You Need for <span className="gradient-text">Data Intelligence</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            A complete AI-powered analytics platform that transforms raw data into actionable business insights.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="group p-6 rounded-xl border border-border/50 bg-card hover:border-primary/30 hover:glow-sm transition-all duration-300"
            >
              <div className="h-10 w-10 rounded-lg gradient-bg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className="h-5 w-5 text-primary-foreground" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
