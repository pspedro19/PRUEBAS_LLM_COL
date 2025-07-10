import React from 'react';

export default function EpicAvatar({ src, alt, rank }: { src: string; alt?: string; rank?: string }) {
  return (
    <div className="relative w-24 h-24 rounded-full border-4 border-gold shadow-lg bg-mysticPurple-dark flex items-center justify-center overflow-hidden">
      <img src={src} alt={alt || 'Avatar'} className="w-full h-full object-cover" />
      {rank && (
        <span className="absolute bottom-0 right-0 bg-gold text-carbon text-xs font-bold px-2 py-1 rounded-tl-lg shadow-md">
          {rank}
        </span>
      )}
    </div>
  );
} 