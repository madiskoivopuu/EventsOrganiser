import { EventDetails, EventTag } from "@/interfaces/global_interfaces";
import { EventAccordion, EventsList } from "./components";
import { useEffect, useState } from "react";
import { useEventsStore } from '@/hooks';

import "./home-page.css";
import { SearchBar } from "./components/SearchBar";
import { SearchOptions } from "./components/SearchBar/SearchBar";
import * as helpers from "./homePageHelpers";
import { ActiveTab } from "./homePageHelpers"; 

interface HomePageProps {
	allTags: EventTag[],
	loadEvents?: undefined, // TODO: 
}

export default function HomePage({ allTags }: HomePageProps) {
	const {events, addOrUpdate} = useEventsStore();
	useEffect(() => {
		addOrUpdate(helpers.__events);
	}, []);
	
	const [activeTab, setActiveTab] = useState<ActiveTab>(ActiveTab.ONGOING);
	const [cachedSearchOpts, setCachedSearchOpts] = useState<SearchOptions>({});
	const [filteredEvents, setFilteredEvents] = useState<EventDetails[]>([]);

	const onSearchChanged = (opts: SearchOptions) => {
		let tabEvents = helpers.filterEventsForTab(events, activeTab);
		let searchFilteredEvents = helpers.applySearchQuery(tabEvents, opts);

		setCachedSearchOpts(opts);
		setFilteredEvents(searchFilteredEvents);
	};

	const onTabChanged = (newTab: ActiveTab) => {
		let tabEvents = helpers.filterEventsForTab(events, newTab);
		let searchFilteredEvents = helpers.applySearchQuery(tabEvents, cachedSearchOpts);

		setActiveTab(newTab);
		setFilteredEvents(searchFilteredEvents);
	};

	useEffect(() => {
		setFilteredEvents(helpers.filterEventsForTab(events, activeTab));
	}, [events]);

    return (
        <div className="container" style={{height: "100%", display: "flex", justifyContent: "center", alignItems: "center"}}>
            <div className="card events-card">
				<SearchBar searchCallback={onSearchChanged} selectableTags={allTags} />
				<div>
					{ /* tabs */ }
					<ul className="tabs" style={{display: "flex", justifyContent: "center"}}>
						<li className={"tab-item" + (activeTab === ActiveTab.PAST ? " active" : "") } onClick={() => onTabChanged(ActiveTab.PAST)}>PAST EVENTS</li>
						<li className={"tab-item" + (activeTab === ActiveTab.ONGOING ? " active" : "") } onClick={() => onTabChanged(ActiveTab.ONGOING)}>ONGOING</li>
						<li className={"tab-item" + (activeTab === ActiveTab.UPCOMING ? " active" : "") } onClick={() => onTabChanged(ActiveTab.UPCOMING)}>UPCOMING EVENTS</li>
					</ul>

					<EventsList events={filteredEvents} allTags={allTags} style={{overflowY: "auto", height: "30rem"}} />
			
					<button>Load more</button>
				</div>
            </div>
        </div>
    );
}