import { useEffect, useState } from "react";
import api from "../api/client";

export default function IssueKey() {
  const [objectCode, setObjectCode] = useState("");
  const user = JSON.parse(localStorage.getItem("user"));
  const [fio, setFio] = useState(user?.full_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [organization, setOrganization] = useState(user?.organization || "");
  const [photo, setPhoto] = useState(null);

  useEffect(() => {
    loadMe();
  }, []);

const loadMe = async () => {
  try {
    const res = await api.get("/auth/me");

    setFio(res.data.full_name || res.data.email || "");
    setPhone(res.data.phone || "");
    setOrganization(res.data.organization || "");
  } catch (e) {
    console.error(e);
  }
};

const handleSubmit = async (e) => {
    e.preventDefault();

    if (!photo) {
      alert("Выбери фото");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("object_code", objectCode);
      formData.append("fio", fio);
      formData.append("organization", organization);
      formData.append("phone", phone);
      formData.append("photo", photo);

      const res = await api.post("/keys/issue", formData);

      alert(res.data.message || "Ключ успешно выдан");

      setObjectCode("");
      setPhoto(null);
      await loadMe();
    } catch (e) {
      console.error(e);
      alert(e.response?.data?.detail || "Ошибка при выдаче ключа");
    }
  };

  return (
    <div>
      <h2>Выдача ключа</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Код объекта</label>
          <br />
          <input
            value={objectCode}
            onChange={(e) => setObjectCode(e.target.value.toUpperCase())}
            placeholder="CH1234"
            maxLength={6}
          />
        </div>

        <div>
          <label>ФИО</label>
          <br />
          <input
            value={fio}
            onChange={(e) => setFio(e.target.value)}
            placeholder="Иванов Иван Иванович"
          />
        </div>

        <div>
          <label>Организация</label>
          <br />
          <input
            value={organization}
            onChange={(e) => setOrganization(e.target.value)}
            placeholder="ООО Ромашка"
          />
        </div>

        <div>
          <label>Телефон</label>
          <br />
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+79990000000"
          />
        </div>

        <div>
          <label>Фото</label>
          <br />
          <input
            type="file"
            accept="image/png,image/jpeg"
            onChange={(e) => setPhoto(e.target.files[0])}
          />
        </div>

        <br />

        <button type="submit">Выдать ключ</button>
      </form>
    </div>
  );
}