import React, { Component } from 'react';
import './App.css';
import xhr from 'xhr';

var API_KEY = 'a77b3a94114bd84600f46a503b688512';

class App extends Component {
  state = {
    location:'',
    data:{}
  };

  fetchData = (evt) => {
      evt.preventDefault();
      console.log('fetch data');
      console.log('current_location', this.state.location);
    var location = encodeURIComponent(this.state.location);
    var urlPrefix = 'http://api.openweathermap.org/data/2.5/forecast?q=';
    var urlSuffix = '&APPID='+API_KEY+'&units=metric';
    var url = urlPrefix + location + urlSuffix;

    var self = this;

    xhr({
        url:url
    }, function(err, data){
        self.setState({
            data:JSON.parse(data.body)
        })
    });

  }

  changeLocation = (evt) => {
      this.setState({
          location: evt.target.value
      });
  }

  render() {
    var currentTemp = 'not loaded yet';
    if(this.state.data.list){
        currentTemp = this.state.data.list[0].main.temp;
    }
    return (
        <div>
        <h1>Weather</h1>
        <form onSubmit={this.fetchData}>
            <label>
                <input
                placeholder="City, Country"
                value={this.state.location}
                onChange={this.changeLocation}
                type="text"/>
            </label>
        </form>
        <p className="tempWrapper">
            <span className="temp">{ currentTemp }</span>
            <span className="temp-symbol">C</span>
        </p>
        </div>
    );
  }
}

export default App;



