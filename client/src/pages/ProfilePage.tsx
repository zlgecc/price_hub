import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getItems } from "../api/client";
import { GlassPanel } from "../components/GlassPanel";
import { PageHeader } from "../components/PageHeader";
import { PriceTable } from "../components/PriceTable";
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
      <GlassPanel padding="lg">
        <PageHeader
          title="个人中心"
          description="订阅数据保存在浏览器 localStorage（MVP 阶段无需登录）"
        />
      </GlassPanel>

      {subscriptions.length === 0 ? (
        <GlassPanel className="text-center">
          <p className="text-slate-500">你还没有订阅任何价格</p>
          <Link to="/catalog" className="glass-button glass-button--primary mt-6 inline-flex">
            去价格目录看看
          </Link>
        </GlassPanel>
      ) : (
        <GlassPanel>
          <div className="mb-5 flex items-center justify-between">
            <p className="text-sm text-slate-500">已订阅 {subscriptions.length} 个品种</p>
          </div>
          {loading ? (
            <div className="loading-shimmer h-48" />
          ) : (
            <div className="space-y-2">
              <PriceTable items={items} showSubscribe={false} />
              <div className="flex flex-wrap gap-2 pt-2">
                {items.map((item) => (
                  <button
                    key={item.code}
                    type="button"
                    onClick={() => remove(item.code)}
                    className="glass-button text-xs text-red-500 hover:text-red-600"
                  >
                    移除 {item.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </GlassPanel>
      )}
    </div>
  );
}
