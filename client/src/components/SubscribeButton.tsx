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
          ? "border-amber-500/30 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20"
          : "border-white/10 bg-white/5 text-slate-400 hover:border-indigo-500/30 hover:bg-white/10 hover:text-indigo-300"
      }`}
    >
      {subscribed ? "已订阅" : "订阅"}
    </button>
  );
}
