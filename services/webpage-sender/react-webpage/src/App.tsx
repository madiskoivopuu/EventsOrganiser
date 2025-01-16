import { useState, useEffect } from 'react'

import "./assets/datepicker/react-datepicker.scss";

import { Sidebar, InputWithIcon } from './components';
import HomePage from './pages/home';
import { EventTag } from './interfaces/global_interfaces';

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
				<HomePage allTags={allPossibleTags} />
			</main>
		</>
	)
}

export default App
