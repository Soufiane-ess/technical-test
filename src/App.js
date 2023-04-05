import React, { useState } from 'react';
import axios from 'axios';
import logo from './logo.svg';
import './App.css';

function App() {

  const [file, setFile] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [responseError, setResponseError] = useState(null);

  const handleFileUpload = event => {
    setFile(event.target.files[0]);
  }
  
  const handleFormSubmit = event => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
    axios.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => {
      setResponseData(response.data)
      setResponseError(null);
      console.log('File uploaded:', response.data);
    }).catch(error => {
      setResponseData(null);
      setResponseError(error.response.data.message)
      console.error('Error uploading file:', error);
    });
  }

 
  return (
    <div className="App">
      <img src={logo} className="App-logo" alt="logo" />
      <p>Upload empire.json</p>
      <form onSubmit={handleFormSubmit}>
        <input type="file" onChange={handleFileUpload} />
        <br/>
        <br/>
        <br/>
        <button type="submit" disabled={!file}>Upload</button>
      </form>

      {responseData && (
        <div>
          {responseData.map((item, index) => (
            <table>
              <thead>
                <tr>
                  <th>Possible path</th>
                  <th>Route</th>
                  <th>Duration</th>
                  <th>Odds</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td></td>
                  <td>{Object.entries(item.route).map(([key, value]) => (<span> {key}: {value} -</span>))}</td>
                  <td>Duration: {item.duration}</td>
                  <td>Odds: <b>{item.odds}</b></td>
                </tr>
              </tbody>
            </table>
          ))}
        </div>
      )}

      {responseError && (
        <div className="error">
          <p>{responseError}</p>
        </div>
      )}

    </div>
  );
}

export default App;