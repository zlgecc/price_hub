import type { Category, Dashboard, ItemDetail, PriceItem } from "../types";

const BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request<T>(path: string): Promise<T> {
  const resp = await fetch(`${BASE}${path}`);
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export function getCategories(): Promise<Category[]> {
  return request("/api/categories");
}

export function getItems(params?: {
  category?: string;
  region?: string;
  search?: string;
}): Promise<PriceItem[]> {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.region) qs.set("region", params.region);
  if (params?.search) qs.set("search", params.search);
  const query = qs.toString();
  return request(`/api/items${query ? `?${query}` : ""}`);
}

export function getItemHistory(code: string, days = 30): Promise<ItemDetail> {
  return request(`/api/items/${code}/history?days=${days}`);
}

export function getDashboard(): Promise<Dashboard> {
  return request("/api/dashboard");
}
