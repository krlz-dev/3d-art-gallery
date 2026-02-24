import { NavLink, useLocation } from 'react-router-dom'

export default function Navbar() {
  const location = useLocation()

  return (
    <nav className="navbar navbar-expand-lg navbar-custom">
      <div className="container">
        <NavLink className="navbar-brand" to="/">
          3D<span>.</span>Gallery
        </NavLink>
        <div className="ms-auto d-flex gap-4">
          {location.pathname === '/' ? (
            <a className="nav-link" href="#gallery">Gallery</a>
          ) : (
            <NavLink className="nav-link" to="/#gallery">Gallery</NavLink>
          )}
          <NavLink
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            to="/about"
          >
            About
          </NavLink>
        </div>
      </div>
    </nav>
  )
}
