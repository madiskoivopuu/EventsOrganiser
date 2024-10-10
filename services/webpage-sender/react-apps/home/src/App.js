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

  ]);
  const [allTags, setAllTags] = useState([]);
  const [searchOpts, setSearchOpts] = useState({
    query: "",
    additionalOptsEnabled: false,
    startDate: null,
    endDate: null,
    tags: []
  })

  const handleSearchOptsChanged = (key, value) => {
    setSearchOpts(prevOpts => (
        {
          ...prevOpts,
          [key]: value
        }
      )
    );
  };

  useEffect(() => {
    fetch("http://localhost:5000/api/events/tags")
    .then(resp => resp.json())
    .then(resp => setAllTags(resp))
    .catch(err => console.log(err));

    var anchorDate = new Date(new Date().toDateString()); // removes time from the date obj
    var queryString = new URLSearchParams({from_time: anchorDate.toISOString(), direction: "forward"}).toString();
    fetch("http://localhost:5000/api/events" + queryString, {
      credentials: "same-origin"
    })
    .then(resp => resp.json())
    .then()
  }, []);

  return (
    <Container>
      <Row>
        <Col sm={12} md={4} xl={3} className="mt-3">
          <SearchBar tags={allTags} activeTabName={activeTab} searchFiltersChanged={handleSearchOptsChanged} />
        </Col>
        <Col sm={12} md={8} xl={9} className="mt-3">
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

          <EventsLister events={events} eventType={activeTab} searchOptions={searchOpts}/>



        </Col>
      </Row>
    </Container>
  );
}

export default App;
