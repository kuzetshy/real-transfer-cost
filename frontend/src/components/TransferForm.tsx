import { ArrowRightLeft, AlertCircle } from "lucide-react";

const CURRENCIES = ["CZK", "EUR", "USD"];

interface TransferFormProps {
  amount: string;
  fromCurr: string;
  toCurr: string;
  loading: boolean;
  error: string | null;
  onAmountChange: (value: string) => void;
  onFromChange: (curr: string) => void;
  onToChange: (curr: string) => void;
  onSwap: () => void;
  onSubmit: () => void;
}

export function TransferForm({
  amount,
  fromCurr,
  toCurr,
  loading,
  error,
  onAmountChange,
  onFromChange,
  onToChange,
  onSwap,
  onSubmit,
}: TransferFormProps) {
  const handleAmountInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (val === "") {
      onAmountChange("");
      return;
    }
    const normalized = val.replace(/^0+(?=\d)/, "");
    if (/^\d*\.?\d*$/.test(normalized)) {
      onAmountChange(normalized);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
      <div className="grid grid-cols-1 md:grid-cols-7 gap-4 items-center">
        {/* Amount */}
        <div className="md:col-span-3 space-y-1">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            You send
          </label>
          <input
            type="text"
            inputMode="decimal"
            value={amount}
            onChange={handleAmountInput}
            placeholder="0"
            className="w-full text-2xl font-bold p-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Source Currency */}
        <div className="md:col-span-1 space-y-1">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            From
          </label>
          <select
            value={fromCurr}
            onChange={(e) => onFromChange(e.target.value)}
            className="w-full text-lg font-semibold p-3.5 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Swap Button */}
        <div className="md:col-span-1 flex justify-center pt-5">
          <button
            onClick={onSwap}
            className="p-3 rounded-full hover:bg-slate-100 transition border border-slate-200 text-slate-600 hover:text-indigo-600"
            title="Swap currencies"
          >
            <ArrowRightLeft className="w-5 h-5" />
          </button>
        </div>

        {/* Target Currency */}
        <div className="md:col-span-1 space-y-1">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            To
          </label>
          <select
            value={toCurr}
            onChange={(e) => onToChange(e.target.value)}
            className="w-full text-lg font-semibold p-3.5 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Submit */}
        <div className="md:col-span-1 pt-5">
          <button
            onClick={onSubmit}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold p-3.5 rounded-xl transition shadow-sm disabled:opacity-50"
          >
            {loading ? "..." : "Compare"}
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-center gap-2 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}
