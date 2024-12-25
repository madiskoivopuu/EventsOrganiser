import { useState } from 'react';

import { LuCalendarDays } from "react-icons/lu";

import "./sidebar-nav.scss"

function SidebarBtn() {

}

function SidebarNavigation() {
  return (
	<>
		<a href="#" className="sidebar-link"> 
			<LuCalendarDays style={{color: "000", marginRight: "0.5rem"}}/> <span>Events</span>
		</a>

		<a href="#" className="sidebar-link link-active"> 
			<LuCalendarDays style={{color: "000", marginRight: "0.5rem"}}/> <span>Settings</span>
		</a>
	</>
  )
}

export default SidebarNavigation;
