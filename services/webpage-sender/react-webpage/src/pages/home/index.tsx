import { EventDetails, EventTag } from "@/interfaces/global_interfaces";
import { EventAccordion } from "./components";
import { useState } from "react";

import "./home-page.css";
import { SearchBar } from "./components/SearchBar";
import { SearchOptions } from "./components/SearchBar/SearchBar";

enum ActiveTab {
	PAST,
	ONGOING,
	UPCOMING,
}

const event: EventDetails = {
	id: 1,
	event_name: "TEST event",
	start_date: "2025-01-01T07:00:00Z",
	end_date: "2025-01-01T22:00:00Z",
	address: "Estonia, Tartu, Raekoja plats",
	tags: [
		{id: 1, name: "Wowe1"},
		{id: 1, name: "Wowe2"},
		{id: 1, name: "Wowe3"},
		{id: 1, name: "Wowe4"},
		{id: 1, name: "Wowe5"},
	]
}

const tags: EventTag[] = [
	{
		id: 1,
		name: "Computer Science"
	},
	{
		id: 2,
		name: "University of Tartu"
	},
]

export default function HomePage() {
	const [filteredEvents, setFilteredEvents] = useState<EventDetails[]>([]);
	const [activeTab, setActiveTab] = useState<ActiveTab>(ActiveTab.ONGOING);

	const onSearchChanged = (opts: SearchOptions) => {

	}

    return (
        <div className="container" style={{height: "100%", display: "flex", justifyContent: "center", alignItems: "center"}}>
            <div className="card events-card" style={{width: "80%", height: "40rem"}}>
				<SearchBar searchCallback={onSearchChanged} selectableTags={tags} />
				<div>
					{ /* tabs */ }
					<ul className="tabs" style={{display: "flex", justifyContent: "center"}}>
						<li role="button" className={"tab-item" + (activeTab === ActiveTab.PAST ? " active" : "") } onClick={() => setActiveTab(ActiveTab.PAST)}>PAST EVENTS</li>
						<li role="button" className={"tab-item" + (activeTab === ActiveTab.ONGOING ? " active" : "") } onClick={() => setActiveTab(ActiveTab.ONGOING)}>ONGOING</li>
						<li role="button" className={"tab-item" + (activeTab === ActiveTab.UPCOMING ? " active" : "") } onClick={() => setActiveTab(ActiveTab.UPCOMING)}>UPCOMING EVENTS</li>
					</ul>

					<EventAccordion event={event} />
				</div>
            </div>
        </div>
    );
}