import { useState } from "react";
import api, { setToken } from "../api/client";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("12345678");

  const handleLogin = async () => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      console.log("LOGIN RESPONSE:", res.data);

      const token = res.data.access_token;

      if (!token) {
        alert("Токен не пришёл от backend");
        return;
      }

      localStorage.setItem("token", token);
      setToken(token);
      onLogin();
    } catch (e) {
      console.error("LOGIN ERROR:", e);
      alert("Ошибка логина");
    }
  };

  return (
    <div>
      <h2>Login</h2>

      <input
        value={email}
        placeholder="email"
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        value={password}
        type="password"
        placeholder="password"
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={handleLogin}>Войти</button>
    </div>
  );
}