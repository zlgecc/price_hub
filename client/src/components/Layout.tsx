import { Link, NavLink, Outlet } from "react-router-dom";

const navClass = ({ isActive }: { isActive: boolean }) =>
  `glass-nav-link ${isActive ? "glass-nav-link--active" : ""}`;

export function Layout() {
  return (
    <>
      <div className="app-background" aria-hidden="true">
        <div className="blur-orb blur-orb--violet" />
        <div className="blur-orb blur-orb--emerald" />
      </div>

      <div className="relative flex min-h-screen flex-col">
        <header className="sticky top-0 z-20 border-b border-white/8 bg-black/40 backdrop-blur-2xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
            <Link to="/" className="flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-sm font-bold text-white">
                PH
              </span>
              <span className="text-lg font-semibold tracking-tight text-white">
                价格中心
                <span className="ml-2 text-sm font-normal text-slate-500">Price Hub</span>
              </span>
            </Link>
            <nav className="flex items-center gap-1">
              <NavLink to="/" end className={navClass}>
                首页
              </NavLink>
              <NavLink to="/catalog" className={navClass}>
                价格目录
              </NavLink>
              <NavLink to="/profile" className={navClass}>
                个人中心
              </NavLink>
            </nav>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 sm:py-10">
          <Outlet />
        </main>

        <footer className="border-t border-white/8 bg-black/30 py-6 text-center text-xs text-slate-500 backdrop-blur-xl">
          数据来源：AKShare · FRED · FreeGoldAPI · TianAPI · 每日自动更新
        </footer>
      </div>
    </>
  );
}
