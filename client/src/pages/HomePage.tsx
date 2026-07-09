import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard } from "../api/client";
import { PriceCard } from "../components/PriceCard";
import type { Dashboard } from "../types";

export function HomePage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboard()
      .then(setDashboard)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-500">加载中...</p>;
  if (error) return <p className="text-red-600">加载失败: {error}</p>;
  if (!dashboard) return null;

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold text-slate-900">今日价格概览</h1>
        <p className="mt-2 text-slate-500">
          贵金属、油价、生活必需品、大宗商品、汇率、股票指数与科技芯片 — 国内外价格每日更新
          {dashboard.updated_at && (
            <span className="ml-2">
              · 最近更新 {new Date(dashboard.updated_at).toLocaleString("zh-CN")}
            </span>
          )}
        </p>
      </section>

      {dashboard.categories.map((cat) => (
        <section key={cat.category_code}>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              {cat.icon} {cat.category_name}
              <span className="ml-2 text-sm font-normal text-slate-400">
                {cat.item_count} 个品种
              </span>
            </h2>
            <Link
              to={`/catalog?category=${cat.category_code}`}
              className="text-sm text-blue-600 hover:underline"
            >
              查看全部 →
            </Link>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {cat.sample_items.map((item) => (
              <PriceCard key={item.code} item={item} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
