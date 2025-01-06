import { IoIosArrowDown } from "react-icons/io";
import { EventDetails } from "@/interfaces/global_interfaces";

import "./event-accordion.scss";
import "./date.scss";

interface ElementProps {
    event: EventDetails
};

interface DateFragmentProps {
    date: string | null,
    threeDots?: boolean
}

function DateFragment({ threeDots, date }: DateFragmentProps) {
    if(!date) 
        return null;
    
    let dayNr: string = new Date(date).toLocaleString('default', { day: '2-digit' });
    let monthShort: string = new Date(date).toLocaleString('default', { month: 'short' }).toUpperCase();
    if(threeDots) {
        dayNr = "&#8203;";
        monthShort = "";
    }
        
    return (
        <div className="event-date">
            <h2>{dayNr}</h2>
            <span>{monthShort}</span>
        </div>
    );
}

function EventDateDisplay({ event }: ElementProps) {
    if(!event.start_date && !event.end_date) {
        console.error("Invalid event start & end date for: ", event);
        return null;
    }

    let startDateElement: JSX.Element | null = <DateFragment date={event.start_date} />;
    let endDateElement: JSX.Element | null = <DateFragment date={event.end_date} />;
    if(!startDateElement && endDateElement) { // deadline type
        startDateElement = <DateFragment threeDots date={""} />
    }

    let lineBetweenDates = startDateElement && endDateElement ? <hr/> : null;

    return (
        <div className="event-date-container">
            {startDateElement}
            {lineBetweenDates}
            {endDateElement}
        </div>
    )
}

function EventAccordion({ event }: ElementProps) {
    return (
        <details className="event-accordion">
            <summary className="event-accordion-header">
                <EventDateDisplay event={event} />

                <div className="event-name">
                    <h2>{event.event_name}</h2>
                </div>

                <div className="dd-icon-container">
                    <IoIosArrowDown className="dd-icon" />
                </div>
            </summary>

            Accordion body
            <br/>
            a
        </details>
    )
}

export default EventAccordion;