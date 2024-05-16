# Air Travel Demand Map

## API Access

### AeroDataBox

🌐 [Academic/Student Access Page](https://aerodatabox.com/students/) \
🌐 [RapidAPI](https://rapidapi.com/hub)

> [!NOTE]
> 50k requests to [Tier 3](https://rapidapi.com/aedbx-aedbx/api/aerodatabox/pricing) has been granted to us for academic use.

We are looking to extract the flight schedule data from all possible airports. This includes where flights are going and how many flights a day occur in all those directions.

```mermaid
flowchart TD;
  id1[<a href='https://doc.aerodatabox.com/#tag/Healthcheck-API/operation/GetFeedAirports'>Healtcheck
  Tier 0</a>]
    -->id2
  id3[Airport/Region]
    -->id2
  id6[Date]
	-->id2
  id2[Airports.json]
    -->id4 & id5
  id4[<a href='https://doc.aerodatabox.com/#tag/Statistical-API/operation/GetRouteDailyStatistics'>Airports routes and daily destinations
  Tier 3</a>]
    -->id7
  id7[Average daily flights matrix]
    -->id11
  id5[<a href='https://doc.aerodatabox.com/#tag/Flight-API/operation/GetAirportFlightsRelative'>FIDS/Schedules
  Tier 2</a>]
    -->id8 & id10
  id8[<a href='https://doc.aerodatabox.com/#tag/Aircraft-API/operation/GetAircraft'>Get single Aircraft
  Tier 1</a>]
    -->
  id9[Aircrafts.json]
    -->
  id10[Average daily seats matrix]
    -->id11
  id11[Average daily passengers per route]
style id1 fill:#bbf,stroke:#000,stroke-width:2px,color:#rfff,stroke-dasharray: 5 5
style id5 fill:#bbf,stroke:#000,stroke-width:2px,color:#rfff,stroke-dasharray: 5 5
style id4 fill:#bbf,stroke:#000,stroke-width:2px,color:#rfff,stroke-dasharray: 5 5
style id8 fill:#bbf,stroke:#000,stroke-width:2px,color:#rfff,stroke-dasharray: 5 5
style id2 fill:#bbb,stroke:#000,stroke-width:2px,color:#rff,stroke-dasharray:
style id7 fill:#bbb,stroke:#000,stroke-width:2px,color:#rff,stroke-dasharray:
style id9 fill:#bbb,stroke:#000,stroke-width:2px,color:#rff,stroke-dasharray:
style id10 fill:#bbb,stroke:#000,stroke-width:2px,color:#rff,stroke-dasharray:
style id11 fill:#bbb,stroke:#000,stroke-width:2px,color:#rff,stroke-dasharray:

```
[*] Input: What data feed is required, in this case: FlightSchedules  
Returns: List of airports (ICAO-codes) that support flight schedules data  

[**] Input: ICAO codes  
Returns: All routes and the amount of flights on those routes for the moment of time from which the data is requested. One airport = one request. This often includes aircraft type. _Note: One request returns statistics based on 7 days prior to the date specified_

A case could be made to use the [FIDS - by local time range](https://doc.aerodatabox.com/#tag/Flight-API/operation/GetAirportFlights) request. 
Input: ICAO code  
Returns: The list of arriving and/or departing flights scheduled and/or planned and/or commenced within a specified time range for a specified airport.

Depending on the number of airports the dataset might be expanded from just one week in summer and one in winter to a broader range.
Airplane data can be received via the 

## Figures

You can plot the [`matplotlib`](https://matplotlib.org) figures in the `figures` directory after installing the `plotting` Conda environment from the provided `environment.yml` file:

```bash
conda env create -f figures/environment.yml
conda activate plotting
```