import { useEffect, useState } from "react";
import "./App.css";
import api, { setToken, setupUnauthorizedHandler } from "./api/client";
import Navbar from "./components/Navbar";
import AdminCreateObject from "./pages/AdminCreateObject";
import AdminHistory from "./pages/AdminHistory";
import IssueKey from "./pages/IssueKey";
import Login from "./pages/Login";
import MyKeys from "./pages/MyKeys";
import Objects from "./pages/Objects";
import AdminUsers from "./pages/AdminUsers";

function App() {
  const [isAuth, setIsAuth] = useState(false);
  const [page, setPage] = useState("objects");
  const [user, setUser] = useState(null);

  const loadMe = async () => {
    const res = await api.get("/auth/me");
    setUser(res.data);
    localStorage.setItem("user", JSON.stringify(res.data));
  };

  useEffect(() => {
    setupUnauthorizedHandler(() => {
      setIsAuth(false);
      setUser(null);
      setPage("objects");
    });

    const token = localStorage.getItem("token");

    if (token) {
      setToken(token);
      setIsAuth(true);
      loadMe().catch(() => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setToken(null);
        setIsAuth(false);
      });
    }
  }, []);

  const handleLogin = async () => {
    setIsAuth(true);
    await loadMe();
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setIsAuth(false);
    setUser(null);
    setPage("objects");
  };

  if (!isAuth) {
    return <Login onLogin={handleLogin} />;
  }

  const isAdmin = user?.role === "admin";

  return (
    <div className="app">
      <Navbar
        setPage={setPage}
        onLogout={logout}
        user={user}
        isAdmin={isAdmin}
      />

      <main className="page">
        {page === "objects" && <Objects />}
        {page === "myKeys" && <MyKeys />}
        {page === "issue" && <IssueKey />}

        {isAdmin && page === "adminCreateObject" && <AdminCreateObject />}
        {isAdmin && page === "adminHistory" && <AdminHistory />}
        {isAdmin && page === "adminUsers" && <AdminUsers />}
      </main>
    </div>
  );
}

export default App;