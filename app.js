import React, { useEffect, useRef, useState } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import OSM from 'ol/source/OSM';
import { fromLonLat } from 'ol/proj';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { Style, Circle, Fill, Stroke, Text } from 'ol/style';
import Heatmap from 'ol/layer/Heatmap';
import './app.css';

function App() {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const vectorSource = useRef(new VectorSource());
  const heatmapSource = useRef(new VectorSource());
  const [activeTab, setActiveTab] = useState('map');
  const [timeAnalysis, setTimeAnalysis] = useState(null);
  const [predictiveAnalysis, setPredictiveAnalysis] = useState(null);
  const [patrolSchedule, setPatrolSchedule] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);

  useEffect(() => {
    // Create map instance if it doesn't exist
    if (!mapInstance.current) {
      mapInstance.current = new Map({
        target: mapRef.current,
        layers: [
          new TileLayer({
            source: new OSM(),
          }),
          new Heatmap({
            source: heatmapSource.current,
            blur: 15,
            radius: 10,
            weight: function(feature) {
              return feature.get('weight');
            }
          }),
          new VectorLayer({
            source: vectorSource.current,
            style: function(feature) {
              const severity = feature.get('severity');
              const crimeType = feature.get('crime_type');
              const location = feature.get('location');
              const radius = severity * 5;
              
              let color;
              switch(crimeType) {
                case 'theft':
                  color = 'rgba(255, 255, 0, 0.6)'; // Yellow
                  break;
                case 'assault':
                  color = 'rgba(255, 0, 0, 0.6)'; // Red
                  break;
                case 'burglary':
                  color = 'rgba(255, 165, 0, 0.6)'; // Orange
                  break;
                case 'robbery':
                  color = 'rgba(255, 0, 0, 0.8)'; // Dark Red
                  break;
                case 'vandalism':
                  color = 'rgba(128, 0, 128, 0.6)'; // Purple
                  break;
                case 'fraud':
                  color = 'rgba(0, 0, 255, 0.6)'; // Blue
                  break;
                default:
                  color = 'rgba(128, 128, 128, 0.6)'; // Gray
              }
              
              return new Style({
                image: new Circle({
                  radius: radius,
                  fill: new Fill({ color }),
                  stroke: new Stroke({ 
                    color: color.replace('0.6', '1'),
                    width: 2 
                  }),
                }),
                text: new Text({
                  text: `${location}\n${crimeType}`,
                  offsetY: -radius - 10,
                  textAlign: 'center',
                  fill: new Fill({ color: '#000' }),
                  stroke: new Stroke({ color: '#fff', width: 3 }),
                })
              });
            }
          }),
        ],
        view: new View({
          center: fromLonLat([80.2707, 13.0827]), // Center on Chennai, Tamil Nadu
          zoom: 12,
        }),
      });

      // Add click handler for features
      mapInstance.current.on('click', function(evt) {
        const feature = mapInstance.current.forEachFeatureAtPixel(evt.pixel, function(feature) {
          return feature;
        });
        
        if (feature) {
          setSelectedLocation({
            location: feature.get('location'),
            crimeType: feature.get('crime_type'),
            severity: feature.get('severity'),
            timestamp: feature.get('timestamp')
          });
        } else {
          setSelectedLocation(null);
        }
      });
    }

    // Fetch crime data
    fetch('http://localhost:5001/api/crime-map')
      .then((res) => res.json())
      .then((data) => {
        const features = JSON.parse(data.features).features;
        features.forEach((feature) => {
          const coord = fromLonLat([feature.properties.lon, feature.properties.lat]);
          const point = new Feature(new Point(coord));
          point.set('crime_type', feature.properties.crime_type);
          point.set('severity', feature.properties.severity);
          point.set('timestamp', feature.properties.timestamp);
          point.set('location', feature.properties.location);
          vectorSource.current.addFeature(point);
          
          // Add to heatmap
          const heatmapPoint = new Feature(new Point(coord));
          heatmapPoint.set('weight', feature.properties.severity);
          heatmapSource.current.addFeature(heatmapPoint);
        });
      });

    // Fetch hotspots
    fetch('http://localhost:5001/api/hotspots')
      .then((res) => res.json())
      .then((data) => {
        data.hotspots.forEach((hotspot) => {
          const coord = fromLonLat([hotspot.lon, hotspot.lat]);
          const point = new Feature(new Point(coord));
          point.set('risk_score', hotspot.risk_score);
          point.set('type', 'hotspot');
          vectorSource.current.addFeature(point);
        });
      });

    return () => {
      // Don't destroy the map, just hide it
      if (mapInstance.current) {
        mapInstance.current.setTarget(null);
      }
    };
  }, []);

  // Show/hide map when tab changes
  useEffect(() => {
    if (mapInstance.current) {
      if (activeTab === 'map') {
        mapInstance.current.setTarget(mapRef.current);
      } else {
        mapInstance.current.setTarget(null);
      }
    }
  }, [activeTab]);

  const fetchSchedule = () => {
    fetch('http://localhost:5001/api/patrol-schedule')
      .then((res) => res.json())
      .then((data) => {
        setPatrolSchedule(data.schedule);
      });
  };

  const fetchTimeAnalysis = () => {
    fetch('http://localhost:5001/api/time-analysis')
      .then((res) => res.json())
      .then((data) => {
        setTimeAnalysis(data);
      });
  };

  const fetchPredictiveAnalysis = () => {
    fetch('http://localhost:5001/api/predictive-analysis')
      .then((res) => res.json())
      .then((data) => {
        setPredictiveAnalysis(data);
      });
  };

  useEffect(() => {
    fetchTimeAnalysis();
    fetchPredictiveAnalysis();
    fetchSchedule();
  }, []);

  const renderTimeAnalysis = () => {
    if (!timeAnalysis) return <div>Loading time analysis...</div>;
    
    return (
      <div className="analysis-container">
        <h2>Time-Based Crime Analysis</h2>
        <div className="analysis-section">
          <h3>Location Analysis</h3>
          <div className="data-grid">
            {Object.entries(timeAnalysis.location_patterns).map(([location, data]) => (
              <div key={location} className="data-item">
                <h4>{location}</h4>
                <p>Most Common Crime: {data.most_common}</p>
                <p>Average Severity: {data.severity_avg.toFixed(1)}</p>
                <p>Total Incidents: {data.count}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="analysis-section">
          <h3>Hourly Patterns</h3>
          <div className="data-grid">
            {Object.entries(timeAnalysis.hourly_patterns).map(([hour, data]) => (
              <div key={hour} className="data-item">
                <h4>{hour}:00 - {hour}:59</h4>
                <p>Incidents: {data.count}</p>
                <p>Most Common: {data.most_common}</p>
                <p>Locations: {data.locations.join(', ')}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="analysis-section">
          <h3>Weekday Patterns</h3>
          <div className="data-grid">
            {Object.entries(timeAnalysis.weekday_patterns).map(([day, data]) => {
              const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
              return (
                <div key={day} className="data-item">
                  <h4>{dayNames[day]}</h4>
                  <p>Incidents: {data.count}</p>
                  <p>Most Common: {data.most_common}</p>
                  <p>Locations: {data.locations.join(', ')}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  const renderPredictiveAnalysis = () => {
    if (!predictiveAnalysis) return <div>Loading predictive analysis...</div>;
    
    return (
      <div className="analysis-container">
        <h2>Predictive Analysis</h2>
        <div className="data-item prediction-summary">
          <h3>Current Risk Assessment</h3>
          <p className={`risk-level risk-${predictiveAnalysis.risk_level.toLowerCase()}`}>
            Overall Risk Level: {predictiveAnalysis.risk_level}
          </p>
          <p>Expected Crime Types: {predictiveAnalysis.expected_crime_types.join(', ')}</p>
          <p>Recent Incidents: {predictiveAnalysis.historical_incidents}</p>
          <div className="risk-factors">
            <h4>Risk Factors</h4>
            {Object.entries(predictiveAnalysis.risk_factors).map(([factor, value]) => (
              <div key={factor} className="risk-factor">
                <span>{factor.replace('_', ' ').toUpperCase()}: </span>
                <span className="risk-value">{value.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderPatrolSchedule = () => {
    if (!patrolSchedule) return <div>Loading patrol schedule...</div>;
    
    return (
      <div className="analysis-container">
        <h2>Patrol Schedule</h2>
        <div className="schedule-grid">
          {patrolSchedule.map((patrol, index) => (
            <div key={index} className={`schedule-item risk-${patrol.risk_level.toLowerCase()}-border`}>
              <h3>{patrol.location}</h3>
              <p>Time: {new Date(patrol.time).toLocaleString()}</p>
              <p>Risk Level: <span className={`risk-${patrol.risk_level.toLowerCase()}`}>
                {patrol.risk_level}
              </span></p>
              <p>Duration: {patrol.patrol_duration}</p>
              <p>Crime Type: {patrol.crime_type}</p>
              <p>Risk Score: {patrol.risk_score.toFixed(2)}</p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      <h1>Crime Mapping - Tamil Nadu</h1>
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'map' ? 'active' : ''}`}
          onClick={() => setActiveTab('map')}
        >
          Crime Map
        </button>
        <button 
          className={`tab ${activeTab === 'time' ? 'active' : ''}`}
          onClick={() => setActiveTab('time')}
        >
          Time Analysis
        </button>
        <button 
          className={`tab ${activeTab === 'predictive' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictive')}
        >
          Predictive Analysis
        </button>
        <button 
          className={`tab ${activeTab === 'patrol' ? 'active' : ''}`}
          onClick={() => setActiveTab('patrol')}
        >
          Patrol Schedule
        </button>
      </div>
      
      <div className="content">
        {activeTab === 'map' && (
          <>
            <div className="map-legend">
              <h3>Crime Types</h3>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: 'rgba(255, 255, 0, 0.6)'}}></span>
                <span>Theft</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: 'rgba(255, 0, 0, 0.6)'}}></span>
                <span>Assault</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: 'rgba(255, 165, 0, 0.6)'}}></span>
                <span>Burglary</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: 'rgba(255, 0, 0, 0.8)'}}></span>
                <span>Robbery</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: 'rgba(128, 0, 128, 0.6)'}}></span>
                <span>Vandalism</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{backgroundColor: 'rgba(0, 0, 255, 0.6)'}}></span>
                <span>Fraud</span>
              </div>
            </div>
            <div ref={mapRef} style={{ width: '100%', height: '500px' }}></div>
            {selectedLocation && (
              <div className="location-details">
                <h3>{selectedLocation.location}</h3>
                <p>Crime Type: {selectedLocation.crimeType}</p>
                <p>Severity: {selectedLocation.severity}</p>
                <p>Time: {selectedLocation.timestamp}</p>
              </div>
            )}
          </>
        )}
        {activeTab === 'time' && renderTimeAnalysis()}
        {activeTab === 'predictive' && renderPredictiveAnalysis()}
        {activeTab === 'patrol' && renderPatrolSchedule()}
      </div>
    </div>
  );
}

export default App;