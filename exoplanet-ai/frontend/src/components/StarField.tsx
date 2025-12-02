import React, { useMemo } from 'react';

interface Star {
  x: number;
  y: number;
  size: number;
  delay: number;
  duration: number;
}

export const StarField: React.FC<{ count?: number }> = ({ count = 200 }) => {
  const stars = useMemo<Star[]>(() => {
    return Array.from({ length: count }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 0.5,
      delay: Math.random() * 3,
      duration: 2 + Math.random() * 3,
    }));
  }, [count]);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Nebula effects */}
      <div className="absolute inset-0 bg-nebula opacity-50" />
      
      {/* Stars */}
      {stars.map((star, i) => (
        <div
          key={i}
          className="absolute rounded-full bg-white"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            animation: `twinkle ${star.duration}s ease-in-out ${star.delay}s infinite`,
            opacity: 0.6 + Math.random() * 0.4,
          }}
        />
      ))}
      
      {/* Shooting star effect */}
      <div className="absolute w-1 h-1 bg-white rounded-full animate-[shootingStar_8s_ease-in-out_infinite]"
           style={{ 
             top: '20%', 
             left: '-10%',
             boxShadow: '0 0 6px 2px rgba(255,255,255,0.6), 100px 0 50px 5px rgba(255,255,255,0.1)'
           }} />
      
      <style>{`
        @keyframes shootingStar {
          0%, 100% { transform: translateX(0) translateY(0); opacity: 0; }
          5% { opacity: 1; }
          10% { transform: translateX(120vw) translateY(30vh); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
