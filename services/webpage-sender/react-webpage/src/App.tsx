import { useState } from 'react'

import "./assets/datepicker/react-datepicker.scss";

import { Sidebar, InputWithIcon } from './components';
import HomePage from './pages/home';

function App() {
  const [startDate, setStartDate] = useState<Date | null>(new Date());
  const [show, setShow] = useState<boolean>(true);

  return (
	<>
		<nav>
			<Sidebar />
		</nav>
		<main>
			<HomePage />
		</main>
	</>
  )
}

export default App
