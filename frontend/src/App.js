import React from 'react';
import logo from './logo.png'
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import { Navbar, NavDropdown, Form, Nav, Button, FormControl, Dropdown } from 'react-bootstrap';

function App() {
  return (
    <div className="App">
      <Navbar bg="light" expand="lg">
        <Navbar.Brand href="#home"><img src={logo} width="110" /></Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="mr-auto">
          </Nav>
          <Form inline>
            <Dropdown drop="left">
              <Dropdown.Toggle variant="primary" id="dropdown-basic">
                Mike Hunt
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <Dropdown.Item href="#/action-2">View surveys</Dropdown.Item>
                <Dropdown.Item href="#/action-3">Sign out</Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </Form>
        </Navbar.Collapse>
      </Navbar>
    </div>
  );
}

export default App;
