import type { ProviderQuote, RateHistoryResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function fetchTransferQuotes(
  fromCurr: string,
  toCurr: string,
  amount: number
): Promise<ProviderQuote[]> {
  const url = `${API_BASE_URL}/api/v1/compare?from_currency=${encodeURIComponent(
    fromCurr
  )}&to_currency=${encodeURIComponent(toCurr)}&amount=${amount}`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error("Failed to fetch transfer quotes.");
  }
  return res.json();
}

export async function fetchRateHistory(
  base: string,
  target: string,
  days: number
): Promise<RateHistoryResponse> {
  const url = `${API_BASE_URL}/api/v1/rates/history?base=${encodeURIComponent(
    base
  )}&target=${encodeURIComponent(target)}&days=${days}`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error("Failed to load historical rate data.");
  }
  return res.json();
}
