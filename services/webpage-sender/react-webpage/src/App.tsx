import { useState } from 'react'
import { IoIosSearch } from "react-icons/io";
import InputWithIcon from "./components/InputWithIcon";
import DatePicker from "react-datepicker";

import "./assets/datepicker/react-datepicker.scss";

import Sidebar from './components/Sidebar/Sidebar';

function App() {
  const [startDate, setStartDate] = useState<Date | null>(new Date());

  return (
	<>
		<nav>
			<Sidebar />
		</nav>
		<main>
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
		</main>
	</>
  )
}

export default App
