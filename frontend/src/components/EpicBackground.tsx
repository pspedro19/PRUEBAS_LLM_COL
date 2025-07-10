import React from 'react';

export default function EpicBackground() {
  return (
    <>
      {/* Fondo base y niebla púrpura animada */}
      <div className="fixed inset-0 z-0 bg-gradient-to-br from-carbon via-mysticPurple to-black opacity-90" />
      {/* Partículas mágicas (placeholder, luego se puede mejorar con canvas o librería) */}
      <div className="pointer-events-none fixed inset-0 z-10 animate-pulse">
        {/* Aquí se pueden renderizar partículas SVG o canvas */}
      </div>
    </>
  );
} 