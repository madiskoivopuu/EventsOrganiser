import { useEffect, useState } from 'react';
import SearchBar from './components/SearchBar';
import EventsLister from './components/EventsLister';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';


function App() {
  const [activeTab, setActiveTab] = useState("ongoing");
  const [events, setEvents] = useState([
    {
      "name": "Three Minute Thesis competition for doctoral students",
      "start_date": new Date("2024-10-02T10:00:00Z"),
      "end_date": new Date("2024-10-02T10:00:00Z"),
      "country": "",
      "city": "Tartu",
      "location": "University of Tartu Library",
      "room": "",
      "tags": ["Presentation"]
    },
    {
      "name": "Delta Career Day",
      "start_date": new Date("2025-02-19T11:00:00Z"),
      "end_date": new Date("2025-02-20T16:00:00Z"),
      "country": "",
      "city": "Tartu",
      "location": "University of Tartu Library",
      "room": "",
      "tags": ["Internships", "Company presentations"]
    }
  ]);

  const handleSearchOptsChanged = () => {
    // TODO
  };

  return (
    <Container>
      <Row>
        <Col sm={12} md={4} xl={3}>
          <SearchBar searchFiltersChanged={handleSearchOptsChanged}/>
        </Col>
        <Col sm={12} md={8} xl={9}>
          <Nav variant="tabs" activeKey={activeTab} justify onSelect={(newKey) => setActiveTab(newKey)}>
            <Nav.Item>
              <Nav.Link eventKey="past">Past</Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="ongoing">Ongoing events</Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="upcoming">Upcoming</Nav.Link>
            </Nav.Item>
          </Nav>

          <EventsLister events={events} eventType={activeTab}/>
        </Col>
      </Row>
    </Container>
  );
}

export default App;
