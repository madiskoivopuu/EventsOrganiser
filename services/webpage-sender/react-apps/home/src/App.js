import { useEffect, useState } from 'react';
import SearchBar from './components/SearchBar';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';


function App() {
  const [activeTab, setActiveTab] = useState("active");
  const [events, setEvents] = useState([]);

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
              <Nav.Link eventKey="active">Ongoing events</Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="upcoming">Upcoming</Nav.Link>
            </Nav.Item>
          </Nav>

        </Col>
      </Row>
    </Container>
  );
}

export default App;
