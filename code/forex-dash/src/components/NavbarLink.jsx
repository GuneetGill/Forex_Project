import React from 'react'
import { NavLink } from 'react-router-dom'

function Navbarlink({path, text}) {
  return (
    <div className = 'navlink'>
        <NavLink to={path} style={{textDecoration: 'none'}}>{text}</NavLink>
    </div>
  )
}

export default Navbarlink