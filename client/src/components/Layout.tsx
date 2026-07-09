import { Link, Outlet } from "react-router-dom";

export function Layout() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="text-xl font-bold text-slate-900">
            价格中心 <span className="text-blue-600">Price Hub</span>
          </Link>
          <nav className="flex gap-4 text-sm font-medium">
            <Link to="/" className="text-slate-600 hover:text-blue-600">
              首页
            </Link>
            <Link to="/catalog" className="text-slate-600 hover:text-blue-600">
              价格目录
            </Link>
            <Link to="/profile" className="text-slate-600 hover:text-blue-600">
              个人中心
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        数据来源：AKShare · FRED · FreeGoldAPI · TianAPI · 每日自动更新
      </footer>
    </div>
  );
}
