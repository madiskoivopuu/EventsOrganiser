import { useState } from 'react'
import { IoIosSearch } from "react-icons/io";
import DatePicker from "react-datepicker";

import "./assets/datepicker/react-datepicker.scss";

import { Sidebar, InputWithIcon } from './components';
import { EventAccordion } from './pages/home/components';
import { EventDetails } from '@/interfaces/global_interfaces';

const event: EventDetails = {
	id: 1,
	event_name: "TEST event",
	start_date: "2024-12-31T21:00:00Z",
	end_date: "2025-01-01T07:00:00Z",
	country: "Estonia",
	city: "Tartu",
	address: "Raekoja plats",
	room: "",
	tags: []
}

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

			<EventAccordion event={ event }/>
		</main>
	</>
  )
}

export default App
