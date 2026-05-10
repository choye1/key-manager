import { useEffect, useState } from "react";
import api from "../api/client";

export default function Objects() {
  const [objects, setObjects] = useState([]);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    const res = await api.get("/objects");
    setObjects(res.data.data);
  };

  return (
    <div>
      <h2>Objects</h2>

      {objects.map((obj) => (
        <div key={obj.id}>
          {obj.code} ({obj.type})
        </div>
      ))}
    </div>
  );
}