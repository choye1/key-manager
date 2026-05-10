import { useState } from "react";
import api from "../api/client";

export default function AdminHistory() {
  const [objectCode, setObjectCode] = useState("");
  const [records, setRecords] = useState([]);

  const loadHistory = async (e) => {
    e.preventDefault();

    try {
      const res = await api.get(`/history/${objectCode}`);
      setRecords(res.data.data);
    } catch (e) {
      console.error(e);
      alert(e.response?.data?.detail || "Ошибка загрузки истории");
      setRecords([]);
    }
  };

  return (
    <div className="card">
      <h2>История операций</h2>

      <form onSubmit={loadHistory}>
        <label>Код объекта</label>
        <input
          value={objectCode}
          onChange={(e) => setObjectCode(e.target.value.toUpperCase())}
          placeholder="CH1234"
          maxLength={6}
        />

        <button type="submit">Показать историю</button>
      </form>

      <hr />

      {records.length === 0 ? (
        <p>История не загружена или записей нет</p>
      ) : (
        records.map((item) => (
          <div className="card" key={item.operation_id}>
            <div className="row">
              <strong>{item.type}</strong>
              <span className="badge">{item.object_code}</span>
            </div>

            <p>ФИО: {item.fio || "-"}</p>
            <p>Организация: {item.organization || "-"}</p>
            <p>Телефон: {item.phone || "-"}</p>
            <p>
              Время операции:{" "}
              {new Date(item.operation_time).toLocaleString()}
            </p>
            <p>Фото: {item.photo_path || "-"}</p>
          </div>
        ))
      )}
    </div>
  );
}