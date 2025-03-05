import { EventDetails, EventTag, ActiveTab } from "@/interfaces/global_interfaces";
import { EventsList } from "./components";
import { useEffect, useState } from "react";
import { useEventPaginationStore, useEventsStore } from '@/hooks';
import "@/assets/datepicker/react-datepicker.scss";

import "./home-page.css";
import { SearchBar } from "./components/SearchBar";
import { SearchOptions } from "./components/SearchBar/SearchBar";
import * as helpers from "./homePageHelpers";
import { EventFetchDirection, getEvents } from "@/apis/events";
import { FinishedFetchingFunc, StartFetchingFunc } from "@/hooks/useEventPaginationStore";
import { toast } from "react-toastify";
import { EventChangerFunc } from "@/hooks/useEventsStore";
import Circles from "react-loading-icons/dist/esm/components/circles";
import TailSpin from "react-loading-icons/dist/esm/components/tail-spin";
import { useShallow } from 'zustand/react/shallow'

let pageLoadTime = new Date().toISOString();

function loadMoreEvents(
	tab: ActiveTab, 
	page: number,
	startFetching: StartFetchingFunc,
	finishedFetching: FinishedFetchingFunc,
	addNewEvents: EventChangerFunc,
) {
	startFetching(tab);

	let direction: EventFetchDirection = tab === ActiveTab.PAST ? "backward" : "forward";
	getEvents(direction, pageLoadTime, page)
	.then(result => {
		addNewEvents(result.items);
		finishedFetching(
			tab, 
			page,
			result.pages
		)
	})
	.catch(err => {
		console.error("Event fetch error", err);
		toast.error(`Failed to fetch ${tab} events for page ${page}`);
	})
}

export default function HomePage() {	
	const [activeTab, setActiveTab] = useState<ActiveTab>(ActiveTab.ONGOING);
	const [cachedSearchOpts, setCachedSearchOpts] = useState<SearchOptions>({});

	const {events, addOrUpdate} = useEventsStore();
	const [currTabPagination, startFetching, finishedFetching] = useEventPaginationStore(useShallow((state) => [state[activeTab], state.startFetching, state.finishedFetching]));

	const onSearchChanged = (opts: SearchOptions) => {
		setCachedSearchOpts(opts);
	};

	useEffect(() => {
		pageLoadTime = new Date().toISOString();

		loadMoreEvents(ActiveTab.PAST, 1, startFetching, finishedFetching, addOrUpdate);
		loadMoreEvents(ActiveTab.UPCOMING, 1, startFetching, finishedFetching, addOrUpdate);

		// TODO: calendar link
	}, []);

	let tabEvents = helpers.filterEventsForTab(events, activeTab);
	let searchFilteredEvents = helpers.applySearchQuery(tabEvents, cachedSearchOpts);

	let loadMoreButton = <></>;
	if(currTabPagination.currPage < currTabPagination.maxPages) {
		loadMoreButton = (
			<button 
				disabled={currTabPagination.isBeingFetched}
				onClick={() => loadMoreEvents(activeTab, currTabPagination.currPage+1, startFetching, finishedFetching, addOrUpdate)}
			>
				{currTabPagination.isBeingFetched && <TailSpin style={{height: "1em"}}/>}
				Load more events
			</button>
		);
	}

    return (
        <div className="container" style={{height: "100%", display: "flex", justifyContent: "center", alignItems: "center"}}>
            <div className="card events-card">
				<SearchBar searchCallback={onSearchChanged}/>
				<div>
					<ul className="tabs" style={{display: "flex", justifyContent: "center"}}>
						<li className={"tab-item" + (activeTab === ActiveTab.PAST ? " active" : "") } onClick={() => setActiveTab(ActiveTab.PAST)}>PAST EVENTS</li>
						<li className={"tab-item" + (activeTab === ActiveTab.ONGOING ? " active" : "") } onClick={() => setActiveTab(ActiveTab.ONGOING)}>ONGOING</li>
						<li className={"tab-item" + (activeTab === ActiveTab.UPCOMING ? " active" : "") } onClick={() => setActiveTab(ActiveTab.UPCOMING)}>UPCOMING EVENTS</li>
					</ul>

					<EventsList events={searchFilteredEvents} tab={activeTab} style={{overflowY: "auto", height: "30rem"}} />
			
					{loadMoreButton}
				</div>
            </div>
        </div>
    );
}