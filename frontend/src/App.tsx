import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import SessionDetail from "./pages/SessionDetail";
import History from "./pages/History";

// TODO: Add a persistent nav/header component
// TODO: Add a global error boundary

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/sessions" element={<History />} />
          <Route path="/sessions/:id" element={<SessionDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
