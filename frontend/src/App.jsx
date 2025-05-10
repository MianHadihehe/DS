import { useState } from 'react'
import Home from './components/Home'
import Predict from './components/Predict'

import {BrowserRouter as Router, Routes, Route } from "react-router-dom"

function App() {

  return (
    <Router>
      <Routes>
        <Route path='/' element={<Home />}></Route>
        <Route path='/prediction' element={<Predict />}></Route>
      </Routes>
      
    </Router>
  )
}

export default App
