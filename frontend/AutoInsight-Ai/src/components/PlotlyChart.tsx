import { useEffect, useRef } from "react";

interface Props {
  data:    any[];
  layout:  any;
  height?: number;
}

const PlotlyChart = ({ data, layout, height = 300 }: Props) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current || !data?.length) return;

    import("plotly.js-dist-min").then((Plotly: any) => {
      Plotly.newPlot(
        ref.current!,
        data,
        {
          ...layout,
          height,
          paper_bgcolor: "transparent",
          plot_bgcolor:  "transparent",
          margin: { l: 30, r: 10, t: 30, b: 40 },
          font: { size: 11 },
        },
        { responsive: true, displayModeBar: false }
      );
    });

    return () => {
      import("plotly.js-dist-min").then((Plotly: any) => {
        if (ref.current) Plotly.purge(ref.current);
      });
    };
  }, [data, layout]);

  if (!data?.length) return (
    <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
      No chart data
    </div>
  );

  return <div ref={ref} style={{ width: "100%", height }} />;
};

export default PlotlyChart;