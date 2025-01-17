import { useState, useEffect } from 'react'
import { Route, Routes } from 'react-router';

import { Sidebar } from './components';
import HomePage from './pages/home';
import { EventTag } from './interfaces/global_interfaces';

import "./assets/datepicker/react-datepicker.scss";

const __tags: EventTag[] = [
	{
		id: 1,
		name: "Computer Science"
	},
	{
		id: 2,
		name: "University of Tartu"
	},
]

function App() {
	const [allPossibleTags, setPossibleTags] = useState<EventTag[]>(__tags);

	return (
		<>
			<nav>
				<Sidebar />
			</nav>
			<main>
				<Routes>
					<Route path="/" element={<HomePage allTags={allPossibleTags} />} />
					<Route path="/" element={<>TODO:</>} />
				</Routes>
			</main>
		</>
	)
}

export default App
