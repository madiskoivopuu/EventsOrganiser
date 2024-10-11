import { act, useEffect, useState } from 'react';
import update from 'immutability-helper';

import SearchBar from './components/SearchBar';
import EventsLister from './components/EventsLister';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Nav from 'react-bootstrap/Nav';
import Button from 'react-bootstrap/Button';

import MoonLoader from "react-spinners/MoonLoader";

async function getEvents(direction, page) {
  var anchorDate = new Date(new Date().toDateString()); // removes time from the date obj
  var queryString = new URLSearchParams({from_time: anchorDate.toISOString(), direction: direction, page: page}).toString();

  try {
    var response = await fetch("http://localhost:8000/api/events?" + queryString, {
      credentials: "same-origin"
    })
    var events = await response.json();
    return { events: events.items, maxPages: events.pages };
  } catch(e) {
    return null;
  }
}

function keepOnlyUniqueEvents(events) {
  return [
    ... new Map(
      events.map(event => [event.id, event])
    ).values()
  ]
}

function App() {
  const [activeTab, setActiveTab] = useState("ongoing");
  const [allTags, setAllTags] = useState([]);

  const [events, setEvents] = useState([]);

  const [eventFetchingStatusForTab, setEventFetchingStatus] = useState({
    past: {
      page: 1,
      maxPages: 0,
      isAppLoadingEvents: true,
      lastFetchErrorMsg: null
    },
    upcoming: {
      page: 1,
      maxPages: 0,
      isAppLoadingEvents: true,
      lastFetchErrorMsg: null
    },
    ongoing: { // permanently hide load more button for this tab
      page: 1,
      maxPages: 0
    }
  })

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

  const addEvents = (eventsData, pageNr, tab) => {
    console.log(eventsData);

    if(eventsData == null) {
      return setEventFetchingStatus(prevState => update(prevState, { // mutability helper seems like a good idea here, to update only certain properties of a nested object; https://stackoverflow.com/questions/43040721/how-to-update-nested-state-properties-in-react
        [tab]: {
          isAppLoadingEvents: {$set: false},
          lastFetchErrorMsg: {$set: `Failed to fetch events for ${tab}, page ${pageNr}`},
          maxPages: {$set: pageNr+1}
        }
      }));
    }

    // convert ISO8601 dates to Date obj, otherwise tabs wont work properly
    eventsData.events.forEach(event => {
      event.start_date = new Date(event.start_date);
      event.end_date = new Date(event.end_date);
    });
    
    setEvents(prevEvents => keepOnlyUniqueEvents([...prevEvents, ...eventsData.events]));

    setEventFetchingStatus(prevState => update(prevState, {
      [tab]: {
        page: {$set: pageNr+1},
        maxPages: {$set: eventsData.maxPages},
        isAppLoadingEvents: {$set: false},
        lastFetchErrorMsg: {$set: null}
      }
    }));
  }

  const loadMoreEvents = (currentTab) => {
    setEventFetchingStatus(prevState => update(prevState, {  // mutability helper seems like a good idea here, to update only certain properties of a nested object; https://stackoverflow.com/questions/43040721/how-to-update-nested-state-properties-in-react
        [currentTab]: {
          isAppLoadingEvents: {$set: true}
        }
      })
    );

    var direction = (currentTab === "past") ? "backward" : "forward";
    var pageNr = eventFetchingStatusForTab[currentTab].page;

    getEvents(direction, pageNr).then(data => {
      addEvents(data, pageNr, currentTab);
    })
  }

  useEffect(() => {
    fetch("http://localhost:8000/api/events/tags")
    .then(resp => resp.json())
    .then(resp => setAllTags(resp))
    .catch(err => console.log(err));

    loadMoreEvents("past");
    loadMoreEvents("upcoming");
  }, []);

  console.log(eventFetchingStatusForTab);

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

          {eventFetchingStatusForTab[activeTab].page <= eventFetchingStatusForTab[activeTab].maxPages && (
            <div className="d-flex justify-content-center">
              {eventFetchingStatusForTab[activeTab].isAppLoadingEvents 
                ? <MoonLoader size={30}/>
                : <Button variant="outline-primary" onClick={() => loadMoreEvents(activeTab)}>Load more events</Button>
              }
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export default App;
