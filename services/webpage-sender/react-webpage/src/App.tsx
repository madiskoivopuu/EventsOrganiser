import { useState } from 'react'
import { IoIosSearch } from "react-icons/io";

import InputWithIcon from "./components/InputWithIcon";
import Sidebar from './components/Sidebar';
import SidebarNavigation from './SidebarNavigationTest';
import DatePicker from "react-datepicker";

import "./assets/datepicker/react-datepicker.scss";

function App() {
  const [startDate, setStartDate] = useState<Date | null>(new Date());

  return (
	<>
		<Sidebar>
			<Sidebar.Header style={{textAlign: "center", margin: "1rem", fontWeight: "bold", fontSize: "32px"}}>
				Events Organiser
			</Sidebar.Header>
			<Sidebar.Content>
				<SidebarNavigation></SidebarNavigation>
			</Sidebar.Content>
			<Sidebar.Footer>
				TEXT
			</Sidebar.Footer>
		</Sidebar>
		<div>
			<InputWithIcon className="search-bar" type="text" placeholder="Event name">
			<IoIosSearch className="icon" />
			</InputWithIcon>

			<DatePicker 
				formatWeekDay={name => name.substring(0, 1)} 
				 customInput={
					<InputWithIcon className="search-bar" type="text" placeholder="Event name">
					<IoIosSearch className="icon" />
				</InputWithIcon>
			} 
				selected={startDate} 
				onChange={(date) => setStartDate(date)} 
			/>
		</div>
	</>
  )
}

export default App
