import { useSubscriptions } from "../hooks/useSubscriptions";

interface Props {
  code: string;
}

export function SubscribeButton({ code }: Props) {
  const { isSubscribed, toggle } = useSubscriptions();
  const subscribed = isSubscribed(code);

  return (
    <button
      type="button"
      onClick={() => toggle(code)}
      className={`rounded-xl border px-3 py-1.5 text-xs font-medium transition ${
        subscribed
          ? "border-amber-200/80 bg-amber-50/80 text-amber-700 hover:bg-amber-100/80"
          : "border-slate-200/70 bg-white/60 text-slate-600 hover:border-indigo-200 hover:bg-white hover:text-indigo-600"
      }`}
    >
      {subscribed ? "已订阅" : "订阅"}
    </button>
  );
}
