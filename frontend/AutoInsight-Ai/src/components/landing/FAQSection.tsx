import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    q: "What file formats are supported?",
    a: "AutoInsight AI supports CSV and Excel (.xlsx, .xls) files. We're actively adding support for JSON, Google Sheets, and database connections.",
  },
  {
    q: "How does the AI multi-agent system work?",
    a: "Our system uses specialized AI agents — for data cleaning, feature engineering, analysis, visualization, and insight generation — orchestrated together to deliver comprehensive analysis automatically.",
  },
  {
    q: "Is my data secure?",
    a: "Absolutely. All data is encrypted at rest and in transit. Each user's data is fully isolated, and we never share or use your data for model training.",
  },
  {
    q: "Can I export my dashboards?",
    a: "Yes! Pro users can export dashboards and charts as PDF or PNG, and download processed datasets in CSV format.",
  },
  {
    q: "Do I need technical skills to use it?",
    a: "Not at all. Simply upload your data and our AI handles everything. You can also use the chat interface to ask questions in plain English.",
  },
];

const FAQSection = () => {
  return (
    <section id="faq" className="py-24">
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Frequently Asked <span className="gradient-text">Questions</span>
          </h2>
        </div>

        <Accordion type="single" collapsible className="space-y-3">
          {faqs.map((faq, i) => (
            <AccordionItem
              key={i}
              value={`faq-${i}`}
              className="border border-border/50 rounded-xl px-6 bg-card data-[state=open]:border-primary/30"
            >
              <AccordionTrigger className="text-left font-medium hover:no-underline">
                {faq.q}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {faq.a}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
};

export default FAQSection;
