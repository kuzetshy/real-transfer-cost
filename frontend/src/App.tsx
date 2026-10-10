import { useState, useEffect } from "react";
import type { ProviderQuote } from "./types";
import { fetchTransferQuotes } from "./api/client";
import { TransferForm } from "./components/TransferForm";
import { ProviderList } from "./components/ProviderList";
import { RateHistoryChart } from "./components/RateHistoryChart";

export default function App() {
  const [amount, setAmount] = useState<string>(() => localStorage.getItem("rtc_amount") ?? "0");
  const [fromCurr, setFromCurr] = useState<string>(() => localStorage.getItem("rtc_from_curr") || "CZK");
  const [toCurr, setToCurr] = useState<string>(() => localStorage.getItem("rtc_to_curr") || "EUR");

  const [quotes, setQuotes] = useState<ProviderQuote[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    const numericAmount = parseFloat(amount) || 0;

    if (numericAmount <= 0) {
      setQuotes([]);
      setError(null);
      return;
    }

    if (fromCurr === toCurr) {
      setError("Please select different currencies for transfer.");
      setQuotes([]);
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const data = await fetchTransferQuotes(fromCurr, toCurr, numericAmount);
      setQuotes(data);
    } catch (err: any) {
      setError(err.message || "Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    localStorage.setItem("rtc_amount", amount);
  }, [amount]);

  useEffect(() => {
    localStorage.setItem("rtc_from_curr", fromCurr);
    localStorage.setItem("rtc_to_curr", toCurr);
  }, [fromCurr, toCurr]);

  useEffect(() => {
    handleCompare();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fromCurr, toCurr]);

  const handleSwap = () => {
    setFromCurr(toCurr);
    setToCurr(fromCurr);
  };

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">
            Real Transfer Cost 💸
          </h1>
          <p className="text-slate-600 text-lg">
            Transparent comparison of transfer fees and hidden exchange rate markups
          </p>
        </div>

        {/* Transfer Input Form */}
        <TransferForm
          amount={amount}
          fromCurr={fromCurr}
          toCurr={toCurr}
          loading={loading}
          error={error}
          onAmountChange={setAmount}
          onFromChange={setFromCurr}
          onToChange={setToCurr}
          onSwap={handleSwap}
          onSubmit={handleCompare}
        />

        {/* Rate History Chart */}
        <RateHistoryChart baseCurrency={fromCurr} targetCurrency={toCurr} />

        {/* Comparison Results */}
        <ProviderList
          quotes={quotes}
          loading={loading}
          fromCurr={fromCurr}
          toCurr={toCurr}
        />

      </div>
    </div>
  );
}
