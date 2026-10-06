import { useState, useEffect } from "react";
import { ArrowRightLeft, AlertCircle, Award } from "lucide-react";
import type { ProviderQuote } from "./types";

const CURRENCIES = ["CZK", "EUR", "USD"];

export default function App() {
  const [amount, setAmount] = useState<number>(10000);
  const [fromCurr, setFromCurr] = useState<string>("CZK");
  const [toCurr, setToCurr] = useState<string>("EUR");
  const [quotes, setQuotes] = useState<ProviderQuote[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQuotes = async () => {
    if (fromCurr === toCurr) {
      setError("Выберите разные валюты для перевода");
      setQuotes([]);
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/compare?from_currency=${fromCurr}&to_currency=${toCurr}&amount=${amount}`
      );
      if (!res.ok) throw new Error("Не удалось получить котировки");
      const data: ProviderQuote[] = await res.json();
      setQuotes(data);
    } catch (err: any) {
      setError(err.message || "Ошибка соединения с сервером");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotes();
  }, [fromCurr, toCurr]);

  const handleSwap = () => {
    setFromCurr(toCurr);
    setToCurr(fromCurr);
  };

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Заголовок */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">
            Real Transfer Cost 💸
          </h1>
          <p className="text-slate-600 text-lg">
            Честное сравнение комиссий и скрытых наценок на курс
          </p>
        </div>

        {/* Форма ввода суммы и валют */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
          <div className="grid grid-cols-1 md:grid-cols-7 gap-4 items-center">
            
            {/* Сумма */}
            <div className="md:col-span-3 space-y-1">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Сумма отправки
              </label>
              <input
                type="number"
                value={amount}
                min={1}
                onChange={(e) => setAmount(Number(e.target.value))}
                className="w-full text-2xl font-bold p-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Валюта отправки */}
            <div className="md:col-span-1 space-y-1">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Из
              </label>
              <select
                value={fromCurr}
                onChange={(e) => setFromCurr(e.target.value)}
                className="w-full text-lg font-semibold p-3.5 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {CURRENCIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Кнопка Swap */}
            <div className="md:col-span-1 flex justify-center pt-5">
              <button
                onClick={handleSwap}
                className="p-3 rounded-full hover:bg-slate-100 transition border border-slate-200 text-slate-600 hover:text-indigo-600"
                title="Поменять местами"
              >
                <ArrowRightLeft className="w-5 h-5" />
              </button>
            </div>

            {/* Валюта получения */}
            <div className="md:col-span-1 space-y-1">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                В
              </label>
              <select
                value={toCurr}
                onChange={(e) => setToCurr(e.target.value)}
                className="w-full text-lg font-semibold p-3.5 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {CURRENCIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Кнопка расчета */}
            <div className="md:col-span-1 pt-5">
              <button
                onClick={fetchQuotes}
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold p-3.5 rounded-xl transition shadow-sm disabled:opacity-50"
              >
                {loading ? "..." : "Расчёт"}
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

        {/* Результаты / Карточки провайдеров */}
        <div className="space-y-4">
          {quotes.map((quote, idx) => {
            const isBest = idx === 0;
            return (
              <div
                key={quote.provider_name}
                className={`relative bg-white rounded-2xl p-6 border transition shadow-sm ${
                  isBest
                    ? "border-emerald-500 ring-2 ring-emerald-500/20"
                    : "border-slate-200 hover:border-slate-300"
                }`}
              >
                {isBest && (
                  <div className="absolute -top-3 left-6 bg-emerald-500 text-white text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full flex items-center gap-1 shadow-sm">
                    <Award className="w-3.5 h-3.5" /> Лучшее предложение
                  </div>
                )}

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-1">
                  <div>
                    <h3 className="text-xl font-bold text-slate-800 capitalize">
                      {quote.provider_name}
                    </h3>
                    <p className="text-sm text-slate-500 mt-0.5">
                      Курс обмена: 1 {fromCurr} = {quote.exchange_rate} {toCurr}
                    </p>
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-black text-slate-900">
                      {Number(quote.received_amount).toLocaleString("ru-RU", { maximumFractionDigits: 2 })} {toCurr}
                    </div>
                    <div className="text-xs text-slate-500">
                      Получатель получит на счёт
                    </div>
                  </div>
                </div>

                <hr className="my-4 border-slate-100" />

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-slate-600">
                  <div>
                    <span className="text-slate-400 block">Комиссия сервиса:</span>
                    <span className="font-semibold">{Number(quote.transfer_fee).toFixed(2)} {fromCurr}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Скрытая наценка:</span>
                    <span className={`font-semibold ${Number(quote.hidden_markup_fee) > 0 ? "text-amber-600" : "text-emerald-600"}`}>
                      {Number(quote.hidden_markup_fee).toFixed(2)} {fromCurr}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Эффективный курс:</span>
                    <span className="font-semibold">{Number(quote.effective_rate).toFixed(4)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
