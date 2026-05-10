export default function Navbar({ setPage, onLogout, user, isAdmin }) {
  return (
    <nav
      style={{
        background: "#111827",
        color: "white",
        padding: "14px 24px",
        display: "flex",
        gap: "12px",
        alignItems: "center",
      }}
    >
      <strong style={{ marginRight: "20px" }}>Key Manager</strong>

      <button onClick={() => setPage("objects")}>Объекты</button>
      <button onClick={() => setPage("myKeys")}>Мои ключи</button>
      <button onClick={() => setPage("issue")}>Выдать ключ</button>

      {isAdmin && (
        <>
          <button onClick={() => setPage("adminCreateObject")}>
            Создать объект
          </button>

          <button onClick={() => setPage("adminHistory")}>История</button>

          <button onClick={() => setPage("adminUsers")}>Пользователи</button>
        </>
      )}

      <span style={{ marginLeft: "auto" }}>
        {user?.full_name || user?.email} ({user?.role})
      </span>

      <button className="danger" onClick={onLogout}>
        Выйти
      </button>
    </nav>
  );
}