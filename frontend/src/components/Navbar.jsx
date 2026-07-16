import React from 'react';
import { NavLink } from 'react-router-dom';

function HomeIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function GroupIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

export default function Navbar({ hiddenOnMobile }) {
  return (
    <nav className={`navbar ${hiddenOnMobile ? 'navbar--hidden-mobile' : ''}`} id="main-navbar">
      <NavLink
        to="/"
        end
        className={({ isActive }) => `navbar-item ${isActive ? 'active' : ''}`}
        id="nav-home"
      >
        <HomeIcon />
      </NavLink>
      <NavLink
        to="/close-friends"
        className={({ isActive }) => `navbar-item ${isActive ? 'active' : ''}`}
        id="nav-close-friends"
      >
        <GroupIcon />
      </NavLink>
    </nav>
  );
}
