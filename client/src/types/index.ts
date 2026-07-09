export interface Category {
  id: number;
  code: string;
  name: string;
  icon: string;
}

export interface PriceItem {
  id: number;
  code: string;
  name: string;
  unit: string;
  source: string;
  region: string;
  category_code: string;
  category_name: string;
  latest_price: number | string | null;
  change_pct: number | string | null;
  record_date: string | null;
}

export interface PriceRecord {
  record_date: string;
  price: number | string;
  change_pct: number | string | null;
}

export interface ItemDetail extends PriceItem {
  history: PriceRecord[];
}

export interface DashboardCategorySummary {
  category_code: string;
  category_name: string;
  icon: string;
  item_count: number;
  sample_items: PriceItem[];
}

export interface Dashboard {
  categories: DashboardCategorySummary[];
  updated_at: string | null;
}
