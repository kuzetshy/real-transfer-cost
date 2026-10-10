import { Award } from "lucide-react";
import type { ProviderQuote } from "../types";

interface ProviderCardProps {
  quote: ProviderQuote;
  isBest: boolean;
  fromCurr: string;
  toCurr: string;
}

export function ProviderCard({ quote, isBest, fromCurr, toCurr }: ProviderCardProps) {
  return (
    <div
      className={`relative bg-white rounded-2xl p-6 border transition shadow-sm ${
        isBest
          ? "border-emerald-500 ring-2 ring-emerald-500/20"
          : "border-slate-200 hover:border-slate-300"
      }`}
    >
      {isBest && (
        <div className="absolute -top-3 left-6 bg-emerald-500 text-white text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full flex items-center gap-1 shadow-sm">
          <Award className="w-3.5 h-3.5" /> Best Offer
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-1">
        <div>
          <h3 className="text-xl font-bold text-slate-800 capitalize">
            {quote.provider_name}
          </h3>
          <p className="text-sm text-slate-500 mt-0.5">
            {quote.description ||
              `Effective rate: 1 ${fromCurr} = ${Number(quote.effective_rate).toFixed(4)} ${toCurr}`}
          </p>
        </div>

        <div className="text-right">
          <div className="text-2xl font-black text-slate-900">
            {Number(quote.received_amount).toLocaleString("en-US", {
              maximumFractionDigits: 2,
            })}{" "}
            {toCurr}
          </div>
          <div className="text-xs text-slate-500">Recipient gets</div>
        </div>
      </div>

      <hr className="my-4 border-slate-100" />

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-slate-600">
        <div>
          <span className="text-slate-400 block">Total fee:</span>
          <span className="font-semibold">{Number(quote.total_fee_czk).toFixed(2)} CZK</span>
        </div>
        <div>
          <span className="text-slate-400 block">Hidden FX markup:</span>
          <span
            className={`font-semibold ${
              Number(quote.markup_loss_czk) > 0 ? "text-amber-600" : "text-emerald-600"
            }`}
          >
            {Number(quote.markup_loss_czk).toFixed(2)} CZK
          </span>
        </div>
        <div>
          <span className="text-slate-400 block">Effective rate:</span>
          <span className="font-semibold">{Number(quote.effective_rate).toFixed(4)}</span>
        </div>
      </div>
    </div>
  );
}
