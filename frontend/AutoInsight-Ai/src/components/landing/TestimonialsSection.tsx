import { Star } from "lucide-react";
import { motion } from "framer-motion";

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Data Scientist at Finova",
    content: "AutoInsight AI replaced hours of manual analysis. The multi-agent system caught patterns our team missed entirely.",
    avatar: "SC",
  },
  {
    name: "Marcus Rivera",
    role: "Head of Analytics, RetailPlus",
    content: "The auto-generated dashboards are production-ready. We went from raw CSV to executive presentation in minutes.",
    avatar: "MR",
  },
  {
    name: "Dr. Aisha Patel",
    role: "Research Lead, BioInsight",
    content: "The chat interface is game-changing. I can explore datasets conversationally without writing a single query.",
    avatar: "AP",
  },
];

const TestimonialsSection = () => {
  return (
    <section className="py-24">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Loved by <span className="gradient-text">Data Teams</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl border border-border/50 bg-card"
            >
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, j) => (
                  <Star key={j} className="h-4 w-4 fill-primary text-primary" />
                ))}
              </div>
              <p className="text-sm text-muted-foreground mb-4 leading-relaxed">"{t.content}"</p>
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-full gradient-bg flex items-center justify-center text-xs font-bold text-primary-foreground">
                  {t.avatar}
                </div>
                <div>
                  <div className="text-sm font-medium">{t.name}</div>
                  <div className="text-xs text-muted-foreground">{t.role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
