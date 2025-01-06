import { IoIosArrowDown } from "react-icons/io";
import { EventDetails } from "@/interfaces/global_interfaces";

import "./event-accordion.scss";
import "./date.scss";
import { useState } from "react";

const formatVenue = (event: EventDetails) => {
    let nonNullLocations: string[] = [event.country, event.city, event.address, event.room].filter(loc => loc !== "");
    return nonNullLocations.join(", ");
}

const formatTags = (event: EventDetails) => {
    let tagNames: string[] = event.tags.map(tag => tag.name);
    return tagNames.join(", ");
}

interface TimeFragmentProps {
    header: string,
    text: string | null
}

function EventDetailFragment({ header, text }: TimeFragmentProps) {
    let displayedText: string = text ? text : "N/A";

    return (
        <div className="event-detailed-info">
            <h3>{header}</h3>
            <span>{displayedText}</span>
        </div>
    )
}

interface DateFragmentProps {
    date: string | null,
    threeDots?: boolean
}

function DateFragment({ threeDots, date }: DateFragmentProps) {
    if(!date) 
        return null;
    
    let dayNr: string = new Date(date).toLocaleString("default", { day: "2-digit" });
    let monthShort: string = new Date(date).toLocaleString("default", { month: "short" }).toUpperCase();
    
    if(threeDots) {
        dayNr = "...";
        monthShort = " ";
    }
        
    return (
        <div className="event-date">
            <h2>{dayNr}</h2>
            <span>{monthShort}</span>
        </div>
    );
}

interface ElementProps {
    event: EventDetails
};

function EventDateDisplay({ event }: ElementProps) {
    if(!event.start_date && !event.end_date) {
        console.error("Invalid event start & end date for: ", event);
        return null;
    }

    let startDateElement: JSX.Element | null = event.start_date ? <DateFragment date={event.start_date} threeDots={true} /> : null;
    let endDateElement: JSX.Element | null = event.end_date ? <DateFragment date={event.end_date} /> : null;
    if(!startDateElement && endDateElement) { // deadline type
        startDateElement = <DateFragment threeDots={true} date={"-"} />
    }

    let lineBetweenDates = startDateElement && endDateElement ? <hr/> : null;

    return (
        <>
            {startDateElement}
            {lineBetweenDates}
            {endDateElement}
        </>
    )
}

function EventAccordion({ event }: ElementProps) {
    const [isBeingEdited, setIsBeingEdited] = useState();

    return (
        <details className="event-accordion">
            <summary className="event-accordion-header">
                <div className="event-date-container">
                    <EventDateDisplay event={event} />
                </div>

                <div className="event-name">
                    <h2>{event.event_name}</h2>
                </div>

                <div className="dd-icon-container">
                    <IoIosArrowDown className="dd-icon" />
                </div>
            </summary>

            <div className="event-accordion-body">
                <div className="event-details">
                    <EventDetailFragment 
                        header={"Start time"} 
                        text={event.start_date ? new Date(event.start_date).toLocaleString("default", { hour: "2-digit", minute: "2-digit" }) : null} 
                    />
                    <EventDetailFragment 
                        header={"End time"} 
                        text={event.end_date ? new Date(event.end_date).toLocaleString("default", { hour: "2-digit", minute: "2-digit" }) : null} 
                    />
                    <EventDetailFragment 
                        header={"Venue"} 
                        text={formatVenue(event)} 
                    />
                    <EventDetailFragment 
                        header={"Event categories"} 
                        text={formatTags(event)} 
                    />
                </div>
                <div className="event-buttons-container">
                        <div className="event-buttons">
                            <button>Edit</button>
                            <button className="warning">Delete</button>
                        </div>
                    </div>
            </div>
        </details>
    )
}

export default EventAccordion;