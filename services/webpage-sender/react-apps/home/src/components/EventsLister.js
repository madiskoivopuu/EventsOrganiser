import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Stack from 'react-bootstrap/Stack';

import "./EventsLister.css"
import { useMemo } from 'react';
import EventAccordion from './EventAccordion';

// Filters events based on which tab is active.
function filterEventsForTab(events, showEvtType) {
    const currDate = new Date();

    let filtered = [];

    if (showEvtType === "past") {
        filtered = events.filter((event) => event.end_date < currDate);
    } else if (showEvtType === "ongoing") {
        filtered = events.filter((event) => event.start_date <= currDate && currDate <= event.end_date);
    } else if (showEvtType === "upcoming") {
        filtered = events.filter((event) => currDate < event.start_date);
    }

    // sort them based on the current tab so that for the past tab, the most recent event is shown first and least recent as last
    filtered.sort((event1, event2) =>  event1.start_date - event2.start_date);
    if (showEvtType === "past")
        filtered.reverse();

    return filtered;
};

// Groups all events in the same month & year into one group
function groupEventsByYM(events) {
    let groupedByYM = events.reduce((currentGroups, event) => {
        let key = event.start_date.toLocaleString("en-US", { month: "long", year: "numeric" }) // { timeZone: 'UTC' }? all event dates are stored as UTC timestamps in database
        if (!currentGroups.hasOwnProperty(key))
            currentGroups[key] = []

        currentGroups[key].push(event);
        return currentGroups;
    }, {});

    return groupedByYM;
}

function applySearchQuery(events, searchOptions) {
    if(searchOptions.query.length > 1)
        events = events.filter((event) => event.name.toLowerCase().includes(searchOptions.query.toLowerCase()) );
    
    if(searchOptions.additionalOptsEnabled) {
        if(searchOptions.startDate !== null)
            events = events.filter((event) => event.start_date >= searchOptions.startDate);

        if(searchOptions.endDate !== null)
            events = events.filter((event) => event.end_date <= searchOptions.endDate);

        if(searchOptions.tags.length > 0)
            events = events.filter((event) => searchOptions.tags.every(tag => event.tags.includes(tag)));
    }

    return events;
}

function EventsLister({ events, eventType, searchOptions }) {
    const eventsForTab = filterEventsForTab(events, eventType);
    if(eventsForTab.length === 0)
        return (
            <div class="mt-4">
                <p style={{textAlign: "center"}}>No events to list</p>
            </div>
        );

    const searchedEvents = applySearchQuery(eventsForTab, searchOptions);
    if(searchedEvents.length === 0)
        return (
            <div class="mt-4">
                <p style={{textAlign: "center"}}>No events found that match the search query</p>
            </div>
        );
        
    const groupedEventsForTab = groupEventsByYM(searchedEvents);

    return (
        <div class="mt-4">
            <Row>
                <Stack gap={3}>
                    {Object.entries(groupedEventsForTab).map(([header, eventsForMonth]) => {
                        return (
                            <Col xs={12}>
                                <h3>{header}</h3>
                                <hr />

                                {eventsForMonth.map((event) => <EventAccordion event={event} />)}
                            </Col>
                        );
                    })}
                </Stack>
            </Row>
        </div>
    )
}

export default EventsLister;