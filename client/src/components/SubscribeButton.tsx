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
      className={`rounded-lg px-3 py-1 text-xs font-medium transition ${
        subscribed
          ? "bg-amber-100 text-amber-700 hover:bg-amber-200"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      {subscribed ? "已订阅" : "订阅"}
    </button>
  );
}
