import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styling/Home.css';




const Home = () => {

    const navigate = useNavigate();
  
  const handleClick = () =>{
    navigate('/prediction')
  }  
  
  return (
    <div id='container'>
        <h1 className='home-text'>Stroke Prediction Analysis</h1>
        <button id='home-btn' onClick={handleClick}>Move Forward</button>
    </div>
  )
}

export default Home