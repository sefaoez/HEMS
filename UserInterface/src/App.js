import './App.css';
import { Button } from '@material-ui/core';
import { TextField } from '@material-ui/core';
import React from 'react';

const errors = {
  openwb: {
    energieBedarf: true,
    maximalerEnergiebedarf: false,
    abfahrzeit: false,
  },
  webasto: {
    energieBedarf: false,
    maximalerEnergiebedarf: false,
    abfahrzeit: false,
  },
};


// data to send backend from user
const inputFields = {
  openwb: {
    energieBedarf: null,
    maximalerEnergiebedarf: null,
    abfahrzeit: null,
  },
  webasto: {
    energieBedarf: null,
    maximalerEnergiebedarf: null,
    abfahrzeit: null,
  },
};

// data coming from backend, only for visualizing
const mockDataFromBackend = {
  hemsVerbindung: { "openwb": "true", "webasto": "false" },
  autoAngeschlossen: { "openwb": "false", "webasto": "false" },
  ladevorgang: { "openwb": "false", "webasto": "false" },
  ladeleistung: { "openwb": 12321.12, "webasto": 222.66 },
  pvStromAnteil: { "openwb": 77.42, "webasto": 23.55 },
  restZeit: { "openwb": 123, "webasto": 2323 },
  durschnittpreisStrom: { "openwb": 123.23, "webasto": 232.22 },
  ladezustand: { "openwb": 2, "webasto": 5 },
};




class App extends React.Component {

  constructor(props) {
    super(props);

    // data from backend
    this.state = {
      inputFields: { ...inputFields },
      ...mockDataFromBackend,
    };

  }

  handleChangeInput = (target, field, value) => {
    const currentState = { ...this.state.inputFields };

    //TODO: check the value
    // if the value is invalid, set error[target][field] = true;
    // then, visualize error

    // changing the value
    currentState[target][field] = value;
    
    
    this.setState({ inputFields: currentState });
  }

  handleCalculate = () => {
    // // mock api call
    // api.calculateResults(this.state.inputFields).then(
    //   (response) => {
    //     // set state accordingly
    //     this.setState({
    //       hemsVerbindung: response.hemsVerbindung,
    //       // TODO: set rest of values
    //     })
    //   }
    // )
  }

  render() {
    return (
      <div id='container' className='container-style'>
        <div class='row'>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gridGap: 10 }}>
            <div>
              <div>
                <div className='center-div'>Eingabe Terminal</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gridGap: 10 }}>
                  <div className='verticaltext'>Openwb</div>
                  <div>
                    <p>Energiebedarf [kWh]:  <TextField error={errors.openwb.energieBedarf} id="standard-basic" label="Standard" onChange={(e) => this.handleChangeInput("openwb", "energieBedarf", e.target.value)} /> </p>
                    <p>Maximaler Energiebedarf [kWh]:  <TextField id="standard-basic" label="Standard" onChange={(e) => this.handleChangeInput("openwb", "maximalerEnergiebedarf", e.target.value)} /> </p>
                    <p>Abfahrzeit:  <TextField id="standard-basic" label="Standard" onChange={(e) => this.handleChangeInput("openwb", "abfahrzeit", e.target.value)} /> </p>
                  </div>
                  <div className='verticaltext'>Webasto</div>
                  <div>
                    <p>Energiebedarf [kWh]:  <TextField id="standard-basic" label="Standard" onChange={(e) => this.handleChangeInput("webasto", "energieBedarf", e.target.value)} /> </p>
                    <p>Maximaler Energiebedarf [kWh]:  <TextField id="standard-basic" label="Standard" onChange={(e) => this.handleChangeInput("webasto", "maximalerEnergiebedarf", e.target.value)} /> </p>
                    <p>Abfahrzeit:  <TextField id="standard-basic" label="Standard" onChange={(e) => this.handleChangeInput("webasto", "abfahrzeit", e.target.value)} /> </p>
                    <div><Button color='primary' onClick={this.handleCalculate} >Calculate</Button></div>
                  </div>
                </div>
              </div>
            </div>
            <div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gridGap: 10, width: 'max-content' }}>
                <div>
                  <div class='row'>Informationen</div>
                  <div class='row'>HEMS - Verbindung</div>
                  <div class='row'>Auto - Angeschlossen</div>
                  <div class='row'>Ladevorgang</div>
                  <div class='row'>Ladeleistung</div>
                  <div class='row'>PV – Strom Anteil</div>
                  <div class='row'></div>
                  <div class='row'>Rest - Zeit</div>
                  <div class='row'>Durchschnittpreis Strom</div>
                  <div class='row'>Ladezustand</div>
                </div>
                <div>
                  <div class='row'>Openwb</div>
                  <div class='row'>{this.state.hemsVerbindung['openwb']}</div>
                  <div class='row'>{this.state.autoAngeschlossen['openwb']}</div>
                  <div class='row'>{this.state.ladevorgang['openwb']}</div>
                  <div class='row'>{this.state.ladeleistung['openwb']}</div>
                  <div class='row'>{this.state.pvStromAnteil['openwb']}</div>
                  <div class='row'></div>
                  <div class='row'>{this.state.restZeit['openwb']}</div>
                  <div class='row'>{this.state.durschnittpreisStrom['openwb']}</div>
                  <div class='row'>{this.state.ladeleistung['openwb']}</div>
                </div>
                <div>
                  <div class='row'>Webasto</div>
                  <div class='row'>{this.state.hemsVerbindung['webasto']}</div>
                  <div class='row'>{this.state.autoAngeschlossen['webasto']}</div>
                  <div class='row'>{this.state.ladevorgang['webasto']}</div>
                  <div class='row'>{this.state.ladeleistung['webasto']}</div>
                  <div class='row'>{this.state.pvStromAnteil['webasto']}</div>
                  <div class='row'></div>
                  <div class='row'>{this.state.restZeit['webasto']}</div>
                  <div class='row'>{this.state.durschnittpreisStrom['webasto']}</div>
                  <div class='row'>{this.state.ladeleistung['webasto']}</div>
                </div>
              </div>
            </div>
            <div>
              <div>
                <div class='row' className='center-div' > Bilanz</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gridGap: 10, width: 'max-content' }}>
                  <div>
                    <div>Aktueller Strompreis:</div>
                    <div>Aktuelle Stromnetzverwendung:</div>
                    <div>Aktuelle Ladekosten:</div>
                    <div>Aktueller Gewinn durch HEMS:</div>
                    <div>Gesamte Ladekosten:</div>
                    <div>Gesamter Gewinn durch HEMS:</div>
                  </div>
                  <div>
                    <div>c./kWh</div>
                    <div>kW</div>
                    <div>€</div>
                    <div>€</div>
                    <div>€</div>
                    <div>€</div>
                  </div>
                </div>
              </div>

              <div>
                <div class='row' className='center-div' > Haus</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gridGap: 10, width: 'max-content' }}>
                  <div>
                    <div>Pv Leistung:</div>
                    <div>Stromverbrauch:</div>
                    <div>Heimsprecher Leistung:</div>
                    <div>Heimsprecher Ladezustand:</div>
                  </div>
                  <div>
                    <div>kW</div>
                    <div>kW</div>
                    <div>kW</div>
                    <div>battery</div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    );
  }
}
export default App;