export interface ProviderQuote {
  provider_name: string;
  sent_amount: number;
  received_amount: number;
  total_fee_czk: number;
  effective_rate: number;
  markup_loss_czk: number;
  description: string;
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