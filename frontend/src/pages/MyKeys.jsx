import { useEffect, useState } from "react";
import api from "../api/client";

export default function MyKeys() {
  const [keys, setKeys] = useState([]);
  const [returningCode, setReturningCode] = useState(null);
  const [photo, setPhoto] = useState(null);

  const [user, setUser] = useState(null);

  const loadMe = async () => {
    const res = await api.get("/auth/me");
    setUser(res.data);
  };

  const loadKeys = async () => {
    try {
      const res = await api.get("/keys/my-issued");
      setKeys(res.data.data);
    } catch (e) {
      console.error(e);
      alert("Не удалось загрузить мои ключи");
    }
  };

  const handleReturn = async () => {
    if (!returningCode) return;

    if (!photo) {
      alert("Выбери фото для возврата");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("object_code", returningCode);
      formData.append("fio", user?.full_name || user?.email || "");
      formData.append("organization", user?.organization || "");
      formData.append("phone", user?.phone || "");
      formData.append("create_new_key_if_no_issued", "false");
      formData.append("photo", photo);

      await api.post("/keys/return", formData);

      alert("Ключ возвращён");
      setReturningCode(null);
      setPhoto(null);
      await loadKeys();
    } catch (e) {
      console.error("RETURN ERROR:", e.response?.data || e);
      alert(JSON.stringify(e.response?.data || "Ошибка возврата ключа"));
    }
  };

  useEffect(() => {
    loadMe();
    loadKeys();
  }, []);

  return (
    <div>
      <h2>Мои ключи</h2>

      {keys.length === 0 ? (
        <div className="card">
          <p>У вас нет выданных ключей</p>
        </div>
      ) : (
        keys.map((key) => (
          <div className="card" key={key.id}>
            <div className="row">
              <h3 style={{ margin: 0 }}>{key.object_code}</h3>
              <span className="badge">{key.status}</span>

              <button
                className="danger"
                style={{ marginLeft: "auto" }}
                onClick={() => {
                  const confirmed = window.confirm(
                    `Вернуть ключ от объекта ${key.object_code}?`
                  );

                  if (confirmed) {
                    setReturningCode(key.object_code);
                  }
                }}
              >
                Вернуть ключ
              </button>
            </div>
          </div>
        ))
      )}

      {returningCode && (
        <div className="card">
          <h3>Возврат ключа от объекта {returningCode}</h3>

          <label>Фото возврата</label>
          <input
            type="file"
            accept="image/png,image/jpeg"
            onChange={(e) => setPhoto(e.target.files[0])}
          />

          <div className="row">
            <button onClick={handleReturn}>Подтвердить возврат</button>

            <button
              className="secondary"
              onClick={() => {
                setReturningCode(null);
                setPhoto(null);
              }}
            >
              Отмена
            </button>
          </div>
        </div>
      )}
    </div>
  );
}