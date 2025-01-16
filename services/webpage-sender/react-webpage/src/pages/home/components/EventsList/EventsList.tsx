import { EventDetails } from "@/interfaces/global_interfaces";
import { EventAccordion } from "../EventAccordion";

interface Dictionary<T> {
    [Key: string]: T
};

const groupEventsByYearAndMonth = (events: EventDetails[]): Dictionary<EventDetails[]> =>  {
    let groupedByYM = events.reduce((currentGroups: Dictionary<EventDetails[]>, event: EventDetails) => {
        if(!event.start_date && !event.end_date) {
            console.error(`groupEventsByYearAndMonth: Error with event ${event.id}, does not have any dates to work with...`);
            return currentGroups;
        }

        let dateToGroupWith: string = (event.start_date || event.end_date)!;
        let key = new Date(dateToGroupWith).toLocaleString("en-US", { month: "long", year: "numeric" }) // { timeZone: 'UTC' }? all event dates are stored as UTC timestamps in database
        if (!currentGroups.hasOwnProperty(key))
            currentGroups[key] = []

        currentGroups[key].push(event);
        return currentGroups;
    }, {});

    return groupedByYM;
}

const sortEvents = (events: EventDetails[]): EventDetails[] => {
    return [ ...events ].sort((a, b) => {
        let aDate: Date = new Date((a.start_date || a.end_date)!);
        let bDate: Date = new Date((a.start_date || a.end_date)!);

        return bDate.valueOf() - aDate.valueOf();
    })
}

interface EventsListProps {
    events: EventDetails[]
};

function EventsList({ events }: EventsListProps) {
    events = sortEvents(events);
    var groupedEvents = groupEventsByYearAndMonth(events);

    var headerAndEvents: JSX.Element[] = Object.entries(groupedEvents).map(([header, events]) => {
        return (
            <>
                <h1>{header}</h1>
                {events.map(event => <EventAccordion key={event.id} event={event} />)}
            </>
        );
    });

    return (
        <>
            {headerAndEvents}
        </>
    )
}

export default EventsList;