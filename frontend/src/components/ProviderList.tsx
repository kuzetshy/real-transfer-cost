import type { ProviderQuote } from "../types";
import { ProviderCard } from "./ProviderCard";

interface ProviderListProps {
  quotes: ProviderQuote[];
  loading: boolean;
  fromCurr: string;
  toCurr: string;
}

export function ProviderList({ quotes, loading, fromCurr, toCurr }: ProviderListProps) {
  if (quotes.length === 0 && !loading) {
    return (
      <div className="text-center py-10 bg-white rounded-2xl border border-dashed border-slate-300 text-slate-400">
        Enter an amount and click <span className="font-semibold text-slate-600">Compare</span> to see transfer options 💡
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {quotes.map((quote, idx) => (
        <ProviderCard
          key={quote.provider_name}
          quote={quote}
          isBest={idx === 0}
          fromCurr={fromCurr}
          toCurr={toCurr}
        />
      ))}
    </div>
  );
}
