import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getItems } from "../api/client";
import { PriceCard } from "../components/PriceCard";
import { useSubscriptions } from "../hooks/useSubscriptions";
import type { PriceItem } from "../types";

export function ProfilePage() {
  const { subscriptions, remove } = useSubscriptions();
  const [items, setItems] = useState<PriceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (subscriptions.length === 0) {
      setItems([]);
      setLoading(false);
      return;
    }
    getItems()
      .then((all) => setItems(all.filter((i) => subscriptions.includes(i.code))))
      .finally(() => setLoading(false));
  }, [subscriptions]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">个人中心</h1>
        <p className="mt-1 text-sm text-slate-500">
          订阅数据保存在浏览器 localStorage（MVP 阶段无需登录）
        </p>
      </div>

      {subscriptions.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 py-16 text-center">
          <p className="text-slate-500">你还没有订阅任何价格</p>
          <Link
            to="/catalog"
            className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            去价格目录看看 →
          </Link>
        </div>
      ) : loading ? (
        <p className="text-slate-500">加载中...</p>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-slate-500">已订阅 {subscriptions.length} 个品种</p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => (
              <div key={item.code} className="relative">
                <PriceCard item={item} showSubscribe={false} />
                <button
                  type="button"
                  onClick={() => remove(item.code)}
                  className="absolute right-3 top-3 rounded bg-white/80 px-2 py-0.5 text-xs text-red-500 hover:bg-red-50"
                >
                  移除
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
