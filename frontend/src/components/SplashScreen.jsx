import React, { useState, useEffect } from 'react';
import logoSrc from '../assets/freinds-logo-mark-pink.svg';

export default function SplashScreen({ onComplete }) {
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    // After animation plays, start exit
    const exitTimer = setTimeout(() => {
      setExiting(true);
    }, 2200);

    // After exit animation, unmount
    const completeTimer = setTimeout(() => {
      onComplete();
    }, 2700);

    return () => {
      clearTimeout(exitTimer);
      clearTimeout(completeTimer);
    };
  }, [onComplete]);

  return (
    <div className={`splash-screen ${exiting ? 'splash-screen--exiting' : ''}`}>
      <img src={logoSrc} alt="FREINDS logo" className="splash-logo" />
      <div className="splash-name">FREINDS</div>
      <p className="splash-tagline">
        Share your best moments with your closest circle
      </p>
    </div>
  );
}
