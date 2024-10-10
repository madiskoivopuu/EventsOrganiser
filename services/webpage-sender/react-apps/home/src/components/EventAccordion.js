import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Accordion from 'react-bootstrap/Accordion';
import Badge from 'react-bootstrap/Badge';

function getTimeDisplayFormat(start_date, end_date) {
    if(start_date === null)
        return <h4>{end_date.toLocaleString("en-US", {month: "short", day: "numeric"})}</h4>;
    else if(end_date === null)
        return <h4>{start_date.toLocaleString("en-US", {month: "short", day: "numeric"})}</h4>;
    else if(start_date.getDate() === end_date.getDate())
        return <h4>{start_date.toLocaleString("en-US", {month: "short", day: "numeric"})}</h4>;
    else
        return (
            <>
                <h4>{start_date.toLocaleString("en-US", {month: "short", day: "numeric"})}</h4>
                <h6>|</h6>
                <h4>{end_date.toLocaleString("en-US", {month: "short", day: "numeric"})}</h4>
            </>
        );
}

function EventAccordion({ event }) {
    const timeDisplayFormat = getTimeDisplayFormat(event.start_date, event.end_date);

    return (
        <Accordion defaultActiveKey="-1" className="mt-1">
            <Accordion.Item>
                <Accordion.Header>
                    <time className="time-display">
                        {timeDisplayFormat}
                    </time>
                    <h2>{event.name}</h2>
                </Accordion.Header>
                <Accordion.Body>
                    <Row>
                        <Col sm={6} md={2}>
                            <strong>Start Time</strong> <br />
                            <span>{event.start_date.toLocaleString("en-US", { hour12: false, month: "short", day: "numeric", hour: "numeric", minute: "numeric" })}</span>
                        </Col>
                        <Col sm={6} md={2}>
                            <strong>End Time</strong> <br />
                            <span>{event.end_date.toLocaleString("en-US", { hour12: false, month: "short", day: "numeric", hour: "numeric", minute: "numeric" })}</span>
                        </Col>
                        <Col sm={12} md={4}>
                            <strong>Location</strong> <br />
                            <span>{ [event.country, event.city, event.address, event.room ].filter(item => Boolean(item)).join(", ") }</span></Col>
                        <Col sm={12} md={4}>
                            <strong>Tags</strong><br />
                            {event.tags.map((tag) => 
                                <Badge pill bg="primary" className="me-1">
                                    {tag}
                                </Badge>
                            )}
                        </Col>
                    </Row>
                </Accordion.Body>
            </Accordion.Item>
        </Accordion>
    );
}

export default EventAccordion;