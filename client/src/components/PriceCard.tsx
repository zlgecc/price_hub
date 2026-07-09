import { Link } from "react-router-dom";
import type { PriceItem } from "../types";
import { changeColor, formatChange, formatPrice } from "../utils/format";
import { SubscribeButton } from "./SubscribeButton";

interface Props {
  item: PriceItem;
  showSubscribe?: boolean;
}

export function PriceCard({ item, showSubscribe = true }: Props) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md">
      <div className="flex items-start justify-between gap-2">
        <div>
          <Link
            to={`/items/${item.code}`}
            className="font-semibold text-slate-900 hover:text-blue-600"
          >
            {item.name}
          </Link>
          <p className="mt-1 text-xs text-slate-500">
            {item.category_name} · {item.region} · {item.source}
          </p>
        </div>
        {showSubscribe && <SubscribeButton code={item.code} />}
      </div>
      <div className="mt-3 flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold text-slate-900">
            {formatPrice(item.latest_price)}
          </p>
          <p className="text-xs text-slate-400">{item.unit}</p>
        </div>
        <p className={`text-sm font-medium ${changeColor(item.change_pct)}`}>
          {formatChange(item.change_pct)}
        </p>
      </div>
      {item.record_date && (
        <p className="mt-2 text-xs text-slate-400">更新于 {item.record_date}</p>
      )}
    </div>
  );
}
