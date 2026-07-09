import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard } from "../api/client";
import { GlassPanel } from "../components/GlassPanel";
import { PageHeader } from "../components/PageHeader";
import { PriceTable } from "../components/PriceTable";
import type { Dashboard } from "../types";

function LoadingState() {
  return (
    <div className="space-y-6">
      <div className="loading-shimmer h-24" />
      <div className="loading-shimmer h-64" />
      <div className="loading-shimmer h-64" />
    </div>
  );
}

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

  if (loading) return <LoadingState />;
  if (error) {
    return (
      <GlassPanel>
        <p className="text-sm text-red-600">加载失败: {error}</p>
      </GlassPanel>
    );
  }
  if (!dashboard) return null;

  const totalItems = dashboard.categories.reduce((sum, cat) => sum + cat.item_count, 0);

  return (
    <div className="space-y-8">
      <GlassPanel padding="lg">
        <PageHeader
          title="今日价格概览"
          description={
            <>
              贵金属、油价、生活必需品、大宗商品、汇率、股票指数与科技芯片 — 国内外价格每日更新
              {dashboard.updated_at && (
                <span className="mt-1 block text-slate-400">
                  最近更新 {new Date(dashboard.updated_at).toLocaleString("zh-CN")}
                </span>
              )}
            </>
          }
        />
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-200/60 bg-white/50 px-5 py-4">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">分类总数</p>
            <p className="mt-2 text-3xl font-semibold tabular-nums text-slate-900">
              {dashboard.categories.length}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200/60 bg-white/50 px-5 py-4">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">品种总数</p>
            <p className="mt-2 text-3xl font-semibold tabular-nums text-slate-900">{totalItems}</p>
          </div>
          <div className="rounded-xl border border-slate-200/60 bg-white/50 px-5 py-4">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">数据状态</p>
            <p className="mt-2 text-lg font-medium text-emerald-600">实时同步</p>
          </div>
        </div>
      </GlassPanel>

      {dashboard.categories.map((cat) => (
        <GlassPanel key={cat.category_code}>
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">
                <span className="mr-2">{cat.icon}</span>
                {cat.category_name}
              </h2>
              <p className="mt-1 text-sm text-slate-500">{cat.item_count} 个品种</p>
            </div>
            <Link to={`/catalog?category=${cat.category_code}`} className="glass-button">
              查看全部
            </Link>
          </div>
          <PriceTable items={cat.sample_items} showCategory={false} compact />
        </GlassPanel>
      ))}
    </div>
  );
}
