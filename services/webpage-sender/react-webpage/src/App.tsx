import { useState } from 'react'
import { IoIosSearch } from "react-icons/io";
import InputWithIcon from "./components/InputWithIcon";
import DatePicker from "react-datepicker";

import "./assets/datepicker/react-datepicker.scss";

function App() {
  const [startDate, setStartDate] = useState<Date | null>(new Date());

  return (
    <div style={{margin: "30px"}}>
        <InputWithIcon className="search-bar" type="text" placeholder="Event name">
          <IoIosSearch className="icon" />
        </InputWithIcon>

        <DatePicker 
          	formatWeekDay={name => name.substring(0, 1)} 
			 /* customInput={
				<InputWithIcon className="search-bar" type="text" placeholder="Event name">
				 <IoIosSearch className="icon" />
			 </InputWithIcon>
		   } */
			selected={startDate} 
			onChange={(date) => setStartDate(date)} 
		/>
    </div>
  )
}

export default App
