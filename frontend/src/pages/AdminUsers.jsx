import { useEffect, useState } from "react";
import api from "../api/client";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [organization, setOrganization] = useState("");
  const [role, setRole] = useState("operator");
  const [password, setPassword] = useState("");

  const loadUsers = async () => {
    try {
      const res = await api.get("/users");
      setUsers(res.data.data);
    } catch (e) {
      console.error(e);
      alert(e.response?.data?.detail || "Ошибка загрузки пользователей");
    }
  };

  const createUser = async (e) => {
    e.preventDefault();

    try {
      await api.post("/users", {
        email,
        full_name: fullName,
        phone,
        organization,
        role,
        is_active: true,
        password,
      });

      alert("Пользователь создан");

      setEmail("");
      setFullName("");
      setPhone("");
      setOrganization("");
      setRole("operator");
      setPassword("");

      await loadUsers();
    } catch (e) {
      console.error(e);
      alert(e.response?.data?.detail || "Ошибка создания пользователя");
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <div>
      <div className="card">
        <h2>Пользователи</h2>

        <form onSubmit={createUser}>
          <label>Email</label>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@example.com"
          />

          <label>ФИО</label>
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Иванов Иван Иванович"
          />

          <label>Телефон</label>
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+79990000000"
          />

          <label>Организация</label>
          <input
            value={organization}
            onChange={(e) => setOrganization(e.target.value)}
            placeholder="ООО Ромашка"
          />

          <label>Роль</label>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="viewer">viewer</option>
            <option value="operator">operator</option>
            <option value="admin">admin</option>
          </select>

          <label>Пароль</label>
          <input
            value={password}
            type="password"
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Минимум 8 символов"
          />

          <button type="submit">Создать пользователя</button>
        </form>
      </div>

      <div className="card">
        <h3>Список пользователей</h3>

        {users.length === 0 ? (
          <p>Пользователей нет</p>
        ) : (
          users.map((user) => (
            <div className="card" key={user.id}>
              <div className="row">
                <strong>{user.full_name || user.email}</strong>
                <span className="badge">{user.role}</span>
                {!user.is_active && <span className="badge">inactive</span>}
              </div>

              <p>Email: {user.email}</p>
              <p>Телефон: {user.phone || "-"}</p>
              <p>Организация: {user.organization || "-"}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}