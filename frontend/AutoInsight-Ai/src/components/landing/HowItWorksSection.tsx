import { Upload, Cpu, LineChart, LayoutDashboard } from "lucide-react";
import { motion } from "framer-motion";

const steps = [
  { icon: Upload, title: "Upload", description: "Drag & drop your CSV or Excel files" },
  { icon: Cpu, title: "Analyze", description: "AI agents clean and process your data" },
  { icon: LineChart, title: "Insights", description: "Get patterns, anomalies, and recommendations" },
  { icon: LayoutDashboard, title: "Dashboard", description: "Auto-generated interactive visualizations" },
];

const HowItWorksSection = () => {
  return (
    <section id="how-it-works" className="py-24 surface">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            How It <span className="gradient-text">Works</span>
          </h2>
          <p className="text-muted-foreground">Four simple steps to transform your data.</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 max-w-5xl mx-auto">
          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="text-center relative"
            >
              <div className="h-16 w-16 rounded-2xl gradient-bg flex items-center justify-center mx-auto mb-4 glow-sm">
                <step.icon className="h-7 w-7 text-primary-foreground" />
              </div>
              <div className="text-xs font-mono text-primary mb-2">Step {i + 1}</div>
              <h3 className="font-semibold text-lg mb-1">{step.title}</h3>
              <p className="text-sm text-muted-foreground">{step.description}</p>

              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-8 left-[60%] w-[80%] border-t border-dashed border-primary/20" />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
