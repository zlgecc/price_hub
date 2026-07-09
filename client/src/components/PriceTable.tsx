import { Link } from "react-router-dom";
import type { PriceItem } from "../types";
import { changeColor, formatChange, formatPrice } from "../utils/format";
import { SubscribeButton } from "./SubscribeButton";

interface Props {
  items: PriceItem[];
  showCategory?: boolean;
  showSubscribe?: boolean;
  compact?: boolean;
  emptyText?: string;
}

export function PriceTable({
  items,
  showCategory = true,
  showSubscribe = true,
  compact = false,
  emptyText = "暂无数据",
}: Props) {
  if (items.length === 0) {
    return (
      <div className="flex min-h-32 items-center justify-center rounded-xl border border-dashed border-slate-200/80 bg-white/30 px-6 py-10 text-sm text-slate-500">
        {emptyText}
      </div>
    );
  }

  const cellPad = compact ? "px-4 py-3" : "px-5 py-4";

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200/60 bg-white/40">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200/70 bg-slate-50/70 text-xs font-medium uppercase tracking-wider text-slate-500">
              <th className={`${cellPad} font-medium`}>品种</th>
              {showCategory && <th className={`${cellPad} font-medium`}>分类</th>}
              <th className={`${cellPad} font-medium`}>地区</th>
              <th className={`${cellPad} font-medium`}>来源</th>
              <th className={`${cellPad} text-right font-medium`}>最新价格</th>
              <th className={`${cellPad} text-right font-medium`}>涨跌</th>
              <th className={`${cellPad} font-medium`}>更新日期</th>
              {showSubscribe && <th className={`${cellPad} text-right font-medium`}>操作</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200/50">
            {items.map((item) => (
              <tr
                key={item.code}
                className="transition-colors hover:bg-white/60"
              >
                <td className={cellPad}>
                  <Link
                    to={`/items/${item.code}`}
                    className="font-medium text-slate-900 transition-colors hover:text-indigo-600"
                  >
                    {item.name}
                  </Link>
                </td>
                {showCategory && (
                  <td className={`${cellPad} text-slate-600`}>{item.category_name}</td>
                )}
                <td className={`${cellPad} text-slate-600`}>{item.region}</td>
                <td className={`${cellPad} text-slate-500`}>{item.source}</td>
                <td className={`${cellPad} text-right`}>
                  <span className="font-semibold tabular-nums text-slate-900">
                    {formatPrice(item.latest_price)}
                  </span>
                  <span className="ml-1 text-xs text-slate-400">{item.unit}</span>
                </td>
                <td className={`${cellPad} text-right`}>
                  <span className={`font-medium tabular-nums ${changeColor(item.change_pct)}`}>
                    {formatChange(item.change_pct)}
                  </span>
                </td>
                <td className={`${cellPad} text-slate-500`}>{item.record_date ?? "—"}</td>
                {showSubscribe && (
                  <td className={`${cellPad} text-right`}>
                    <SubscribeButton code={item.code} />
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
