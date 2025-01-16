import { EventDetails, EventTag } from "@/interfaces/global_interfaces";
import { EventAccordion, EventsList } from "./components";
import { useEffect, useState } from "react";
import { useEventsStore } from '@/hooks';

import "./home-page.css";
import { SearchBar } from "./components/SearchBar";
import { SearchOptions } from "./components/SearchBar/SearchBar";

const __events: EventDetails[] = [
	{
		id: 1,
		event_name: "TEST event",
		start_date: "2025-01-01T07:00:00Z",
		end_date: "2025-01-01T22:00:00Z",
		address: "Estonia, Tartu, Raekoja plats",
		tags: [
			{id: 1, name: "Computer Science"},
			{id: 2, name: "Wowe2"},
			{id: 3, name: "Wowe3"},
			{id: 4, name: "Wowe4"},
			{id: 5, name: "Wowe5"},
		]
	},
	{
		id: 2,
		event_name: "School meeting",
		start_date: "2025-04-01T07:00:00Z",
		end_date: "2025-04-07T22:00:00Z",
		address: "Estonia, Tartu, Raekoja plats",
		tags: [
			{id: 1, name: "Wowe1"},
			{id: 2, name: "Wowe2"},
			{id: 3, name: "Wowe3"},
			{id: 4, name: "Wowe4"},
			{id: 5, name: "Wowe5"},
		]
	},
	{
		id: 3,
		event_name: "Deadline",
		start_date: "",
		end_date: "2025-04-06T22:00:00Z",
		address: "Estonia, Tartu, Raekoja plats",
		tags: [
			{id: 1, name: "Deadline"},
		]
	},
	{
		id: 4,
		event_name: "Deadline",
		start_date: "",
		end_date: "2022-04-06T22:00:00Z",
		address: "Estonia, Tartu, Raekoja plats",
		tags: [
			{id: 1, name: "Deadline"},
		]
	},
	{
		id: 5,
		event_name: "Deadline",
		start_date: "",
		end_date: "2027-04-06T22:00:00Z",
		address: "Estonia, Tartu, Raekoja plats",
		tags: [
			{id: 1, name: "Deadline"},
		]
	},
]

enum ActiveTab {
	PAST,
	ONGOING,
	UPCOMING,
}

const filterEventsForTab = (events: EventDetails[], showEvtType: ActiveTab) => {
    let filtered: EventDetails[] = [];
    const currDate = new Date();

	switch(showEvtType) {
		case ActiveTab.PAST: {
			filtered = events.filter((event) => new Date(event.end_date) < currDate);
			break;
		}
		case ActiveTab.ONGOING: {
			filtered = events.filter((event) => currDate <= new Date(event.end_date) && (!event.start_date || new Date(event.start_date) <= currDate));
			break;
		}
		case ActiveTab.UPCOMING: {
			filtered = events.filter((event) => (event.start_date && currDate < new Date(event.start_date)) || (event.end_date && currDate < new Date(event.end_date)));
			break;
		}
	}

    return filtered;
};

const applySearchQuery = (events: EventDetails[], searchOptions: SearchOptions): EventDetails[] => {
    if(searchOptions.eventName && searchOptions.eventName?.length > 1)
        events = events.filter((event) => event.event_name.toLowerCase().includes(searchOptions.eventName!.toLowerCase()) );
    
	if(searchOptions.startDate)
		events = events.filter((event) => event.start_date && new Date(event.start_date) >= searchOptions.startDate!); // TODO: fix possible bug with events that have no start date

	if(searchOptions.endDate)
		events = events.filter((event) => event.end_date && new Date(event.end_date) <= searchOptions.endDate!);

	if(searchOptions.tags && searchOptions.tags.length > 0)
		events = events.filter((event) => {
			let eventTagIds: Set<number> = new Set(event.tags.map(tag => tag.id));

			return searchOptions.tags!.map(tag => tag.id).every(tagId => eventTagIds.has(tagId))
		});

    return events;
}

interface HomePageProps {
	allTags: EventTag[],
	loadEvents?: undefined, // TODO: 
}

export default function HomePage({ allTags }: HomePageProps) {
	const {events, addOrUpdate} = useEventsStore();
	
	useEffect(() => {
		addOrUpdate(__events);
	}, []);

	const [activeTab, setActiveTab] = useState<ActiveTab>(ActiveTab.ONGOING);
	const [cachedSearchOpts, setCachedSearchOpts] = useState<SearchOptions>({});
	const [filteredEvents, setFilteredEvents] = useState<EventDetails[]>([]);

	const onSearchChanged = (opts: SearchOptions) => {
		let tabEvents = filterEventsForTab(events, activeTab);
		let searchFilteredEvents = applySearchQuery(tabEvents, opts);

		setCachedSearchOpts(opts);
		setFilteredEvents(searchFilteredEvents);
	};

	const onTabChanged = (newTab: ActiveTab) => {
		let tabEvents = filterEventsForTab(events, newTab);
		let searchFilteredEvents = applySearchQuery(tabEvents, cachedSearchOpts);

		setActiveTab(newTab);
		setFilteredEvents(searchFilteredEvents);
	};

	useEffect(() => {
		setFilteredEvents(filterEventsForTab(events, activeTab));
	}, [events]);

    return (
        <div className="container" style={{height: "100%", display: "flex", justifyContent: "center", alignItems: "center"}}>
            <div className="card events-card" style={{width: "80%", height: "40rem"}}>
				<SearchBar searchCallback={onSearchChanged} selectableTags={allTags} />
				<div>
					{ /* tabs */ }
					<ul className="tabs" style={{display: "flex", justifyContent: "center"}}>
						<li className={"tab-item" + (activeTab === ActiveTab.PAST ? " active" : "") } onClick={() => onTabChanged(ActiveTab.PAST)}>PAST EVENTS</li>
						<li className={"tab-item" + (activeTab === ActiveTab.ONGOING ? " active" : "") } onClick={() => onTabChanged(ActiveTab.ONGOING)}>ONGOING</li>
						<li className={"tab-item" + (activeTab === ActiveTab.UPCOMING ? " active" : "") } onClick={() => onTabChanged(ActiveTab.UPCOMING)}>UPCOMING EVENTS</li>
					</ul>

					<EventsList events={filteredEvents} />

					<button>Load more</button>
				</div>
            </div>
        </div>
    );
}