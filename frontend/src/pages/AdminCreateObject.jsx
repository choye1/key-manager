import { useState } from "react";
import api from "../api/client";

export default function AdminCreateObject() {
  const [code, setCode] = useState("");
  const [type, setType] = useState("indoor");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await api.post("/objects", {
        code,
        type,
        is_active: true,
      });

      alert("Объект создан");
      setCode("");
      setType("indoor");
    } catch (e) {
      console.error(e);
      alert(e.response?.data?.detail || "Ошибка создания объекта");
    }
  };

  return (
    <div className="card">
      <h2>Создание объекта</h2>

      <form onSubmit={handleSubmit}>
        <label>Код объекта</label>
        <input
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder="CH1234"
          maxLength={6}
        />

        <label>Тип объекта</label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="indoor">indoor</option>
          <option value="outdoor">outdoor</option>
        </select>

        <button type="submit">Создать объект</button>
      </form>
    </div>
  );
}