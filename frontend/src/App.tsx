import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ResultsPage from "./pages/ResultsPage";
import HistoryPage from "./pages/HistoryPage";

function Nav() {
  return (
    <header className="sticky top-0 z-50 border-b border-dark-600 bg-dark-800">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link to="/" className="font-bold text-lg tracking-tight text-white">
          Podium<span className="text-blue-500">AI</span>
        </Link>
        <nav className="flex items-center gap-6">
          <NavLink
            to="/history"
            className={({ isActive }) =>
              `text-sm transition-colors ${
                isActive ? "text-white" : "text-gray-400 hover:text-white"
              }`
            }
          >
            History
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-dark-900 text-slate-100">
        <Nav />
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/results/:id" element={<ResultsPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
