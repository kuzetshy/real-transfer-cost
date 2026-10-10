import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { TrendingUp, AlertCircle, Loader2 } from "lucide-react";
import type { RateHistoryPoint, RateHistoryResponse } from "../types";

interface RateHistoryChartProps {
  baseCurrency: string;
  targetCurrency: string;
}

const TIMEFRAMES = [
  { label: "7D", days: 7 },
  { label: "30D", days: 30 },
  { label: "90D", days: 90 },
];

export function RateHistoryChart({ baseCurrency, targetCurrency }: RateHistoryChartProps) {
  const [data, setData] = useState<RateHistoryPoint[]>([]);
  const [days, setDays] = useState<number>(30);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      if (baseCurrency === targetCurrency) {
        setData([]);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/v1/rates/history?base=${baseCurrency}&target=${targetCurrency}&days=${days}`
        );

        if (!response.ok) {
          throw new Error("Failed to load historical rate data.");
        }

        const json: RateHistoryResponse = await response.json();
        setData(json.history || []);
      } catch (err: any) {
        setError(err.message || "Failed to load exchange rate history.");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [baseCurrency, targetCurrency, days]);

  if (baseCurrency === targetCurrency) {
    return null;
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-4">
      {/* Header and timeframe selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">
              Exchange Rate History
            </h2>
            <p className="text-xs text-slate-500">
              Mid-market rate trend for {baseCurrency}/{targetCurrency}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl self-start sm:self-auto">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf.days}
              onClick={() => setDays(tf.days)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                days === tf.days
                  ? "bg-white text-indigo-600 shadow-sm"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main chart view states */}
      {loading ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-400 gap-2">
          <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
          <span className="text-xs font-medium">Fetching history points...</span>
        </div>
      ) : error ? (
        <div className="h-64 flex items-center justify-center text-rose-500 gap-2 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      ) : data.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-slate-400 text-sm border border-dashed rounded-xl border-slate-200">
          No historical data points available for this pair yet.
        </div>
      ) : (
        <div className="h-64 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                tickFormatter={(val: string) => {
                  const parts = val.split("-");
                  return parts.length === 3 ? `${parts[1]}/${parts[2]}` : val;
                }}
              />
              <YAxis
                domain={["auto", "auto"]}
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                tickFormatter={(val: number) => val.toFixed(3)}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderRadius: "0.75rem",
                  border: "none",
                  color: "#fff",
                  fontSize: "12px",
                  padding: "8px 12px",
                }}
                labelStyle={{ color: "#94a3b8", marginBottom: "4px" }}
                formatter={(val: any) => [
                  `${Number(val).toFixed(4)} ${targetCurrency}`,
                  `1 ${baseCurrency}`,
                ]}
              />
              <Line
                type="monotone"
                dataKey="rate"
                stroke="#4f46e5"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5, fill: "#4f46e5", stroke: "#ffffff", strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
