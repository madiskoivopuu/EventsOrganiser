import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Stack from 'react-bootstrap/Stack';

import "./EventsLister.css"
import { useMemo } from 'react';
import EventAccordion from './EventAccordion';

function EventsLister({ events, eventType, filterOptions }) {
    const filterAndGroupEvents = (events, showEvtType) => {
        const currDate = new Date();

        let filtered = [];

        if (showEvtType === "past") {
            filtered = events.filter((event) => event.end_date < currDate);
        } else if (showEvtType === "ongoing") {
            filtered = events.filter((event) => event.start_date <= currDate && currDate <= event.end_date);
        } else if (showEvtType === "upcoming") {
            filtered = events.filter((event) => currDate < event.start_date);
        }

        // sort them based on the current tab
        filtered.sort((event1, event2) => event2.start_date - event1.start_date);
        if (showEvtType === "past")
            filtered.reverse();

        // group those events together into their own month
        let groupedByYM = filtered.reduce((currentGroups, event) => {
            let key = event.start_date.toLocaleString("en-US", { month: "long", year: "numeric" }) // { timeZone: 'UTC' }? all event dates are stored as UTC timestamps in database
            if (!currentGroups.hasOwnProperty(key))
                currentGroups[key] = []

            currentGroups[key].push(event);
            return currentGroups;
        }, {});

        return groupedByYM;
    };

    const eventsForTab = filterAndGroupEvents(events, eventType);
    if(Object.keys(eventsForTab).length == 0)
        return (
            <div class="mt-4">
                <p style={{textAlign: "center"}}>No events found</p>
            </div>
        );

    return (
        <div class="mt-4">
            <Row>
                <Stack gap={3}>
                    {Object.entries(eventsForTab).map(([header, eventsForMonth]) => {
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