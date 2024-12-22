import { useState } from 'react'
import { IoIosSearch } from "react-icons/io";
import InputWithIcon from "./components/InputWithIcon";

function App() {
  return (
    <>
        <InputWithIcon className="search-bar" type="text" placeholder="Event name">
          <IoIosSearch className="icon" />
        </InputWithIcon>
    </>
  )
}

export default App
