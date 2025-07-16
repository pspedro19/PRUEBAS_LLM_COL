import React from "react";

export default function AssistantAvatar({ message }: { message: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
      <img
        src="/avatar-profesor.png"
        alt="Profesor"
        style={{ width: 64, height: 64, borderRadius: "50%", marginRight: 16 }}
      />
      <div
        style={{
          background: "#f3f4f6",
          borderRadius: 12,
          padding: "12px 20px",
          fontSize: 16,
          maxWidth: 400,
        }}
      >
        {message}
      </div>
    </div>
  );
} 