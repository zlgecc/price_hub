import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getCategories, getItems } from "../api/client";
import { GlassPanel } from "../components/GlassPanel";
import { PageHeader } from "../components/PageHeader";
import { PriceTable } from "../components/PriceTable";
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
      <GlassPanel padding="lg">
        <PageHeader
          title="价格目录"
          description="浏览全部价格品种，支持按分类、地区筛选与关键词搜索"
        />
      </GlassPanel>

      <GlassPanel>
        <div className="mb-6 flex flex-wrap gap-3">
          <input
            type="text"
            placeholder="搜索品种..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="glass-input min-w-[200px] flex-1"
          />
          <select
            value={category}
            onChange={(e) => {
              const next = new URLSearchParams(searchParams);
              if (e.target.value) next.set("category", e.target.value);
              else next.delete("category");
              setSearchParams(next);
            }}
            className="glass-select"
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
            className="glass-select"
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
          <div className="loading-shimmer h-64" />
        ) : (
          <PriceTable
            items={items}
            emptyText="暂无数据，请先触发价格抓取"
          />
        )}
      </GlassPanel>
    </div>
  );
}
