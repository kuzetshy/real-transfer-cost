export interface ProviderQuote {
  provider_name: string;
  transfer_fee: number;
  exchange_rate: number;
  received_amount: number;
  hidden_markup_fee: number;
  total_cost: number;
  effective_rate: number;
}

export interface RateHistoryPoint {
  date: string;
  rate: number;
}

export interface RateHistoryResponse {
  base_currency: string;
  target_currency: string;
  provider: string;
  points_count: number;
  history: RateHistoryPoint[];
}
