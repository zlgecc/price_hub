import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getCategories, getItems } from "../api/client";
import { PriceCard } from "../components/PriceCard";
import type { Category, PriceItem } from "../types";

export function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [categories, setCategories] = useState<Category[]>([]);
  const [items, setItems] = useState<PriceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(searchParams.get("search") ?? "");

  const category = searchParams.get("category") ?? "";
  const region = searchParams.get("region") ?? "";

  useEffect(() => {
    getCategories().then(setCategories);
  }, []);

  useEffect(() => {
    setLoading(true);
    getItems({ category: category || undefined, region: region || undefined, search: search || undefined })
      .then(setItems)
      .finally(() => setLoading(false));
  }, [category, region, search]);

  const regions = [...new Set(items.map((i) => i.region))].sort();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">价格目录</h1>

      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="搜索品种..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <select
          value={category}
          onChange={(e) => {
            const next = new URLSearchParams(searchParams);
            if (e.target.value) next.set("category", e.target.value);
            else next.delete("category");
            setSearchParams(next);
          }}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
        >
          <option value="">全部分类</option>
          {categories.map((c) => (
            <option key={c.code} value={c.code}>
              {c.icon} {c.name}
            </option>
          ))}
        </select>
        <select
          value={region}
          onChange={(e) => {
            const next = new URLSearchParams(searchParams);
            if (e.target.value) next.set("region", e.target.value);
            else next.delete("region");
            setSearchParams(next);
          }}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
        >
          <option value="">全部地区</option>
          {regions.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-slate-500">加载中...</p>
      ) : items.length === 0 ? (
        <p className="text-slate-500">暂无数据，请先触发价格抓取</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <PriceCard key={item.code} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
