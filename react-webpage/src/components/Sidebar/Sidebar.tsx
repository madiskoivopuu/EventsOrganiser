import { useState } from 'react';
import { LuCalendarDays } from "react-icons/lu";
import { IoMenu, IoSettingsOutline } from "react-icons/io5";
import { MdLogout } from "react-icons/md";
import useFitText from "use-fit-text";
import { NavLink } from "react-router";

import "./sidebar.scss"
import "./sidebar-nav.scss";

function Sidebar() {
	const { fontSize, ref } = useFitText();
	const [isClosed, setIsClosed] = useState<Boolean>(true);

	let sidebarClassname: string = "sidebar";
	if(isClosed)
		sidebarClassname += " closed";

	return (
		<>			
			<div className="sidebar-header header-mobile">
				<IoMenu style={{cursor: "pointer"}} onClick={() => setIsClosed(prev => !prev)}/>

				<span style={{flexGrow: "1"}}>Events Organiser</span>
			</div>

			<div style={{position: "relative"}}>
				<aside className={sidebarClassname}>
					<div className="sidebar-header">
						<span>Events Organiser</span>
					</div>

					<div className="sidebar-content">
						<NavLink to="/" className="sidebar-link"> 
							<LuCalendarDays className="sidebar-btn-icon"/>
							<span>Events</span>
						</NavLink>

						<NavLink to="/settings" className="sidebar-link"> 
							<IoSettingsOutline className="sidebar-btn-icon"/>
							<span>Settings</span>
						</NavLink>
					</div>

					<div className="sidebar-footer" style={{padding: "1rem"}}>
						<div ref={ref} style={{ fontSize }}>
							<b>lorem.ipsum@ut.ee</b>
						</div>
						<a href="#" className="logout-btn">
							<MdLogout />
							Log out
						</a>
					</div>
				</aside>
			</div>
		</>
	)
}

export default Sidebar;
