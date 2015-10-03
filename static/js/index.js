
var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];

function initmap() {
    console.log( "Starting map initialization.");
    // set up AJAX request
    ajaxRequest = getXmlHttpObject();
    if( ajaxRequest == null) {
        alert( "This browser does not support HTTP Request");
        return;
    }
    
 
  // set up the map
  // var map = new L.Map('map');

  // create the tile layer with correct attribution
  var osmUrl="https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6IjZjNmRjNzk3ZmE2MTcwOTEwMGY0MzU3YjUzOWFmNWZhIn0.Y8bhBaUMqFiPrDRW9hieoQ";
  var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
  var osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib, id: 'mapbox.streets'})

  map = L.map('map');
  map.setView([46.233809, 6.055767], 13)
  map.addLayer(osm)

  L.circle([46.233, 6.055], 500, {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5
  }).addTo(map).bindPopup("I am a circle.");
  
  // Plotting pins
  askForPlots();
  map.on('moveend', onMapMove);
  console.log( "Map has been initialized.");
}

function getXmlHttpObject() {
  if( window.XMLHttpRequest) {
      return new XMLHttpRequest();
  }
  if( window.ActiveXObject) {
      return new ActiveXObject( "Microsoft.XMLHTTP");
  }
  return null;
}

function askForPlots() {
    console.log( "Asking for plots.");
  // request the marker info with AJAX for the current bounds
  var bounds = map.getBounds();
  var minll = bounds.getSouthWest();
  var maxll = bounds.getNorthEast();
  var msg = '/events?minlon='+minll.lng+'&minlat='+minll.lat+'&maxlon='+maxll.lng+'&maxlat='+maxll.lat;
  ajaxRequest.onreadystatechange = stateChanged;
  ajaxRequest.open('GET', msg, true);
  ajaxRequest.send(null);
}

function stateChanged() {
    console.log( "State has changed.");
    console.log( "AJAX ready state: " + ajaxRequest.readyState)
    console.log( "AJAX status: " + ajaxRequest.status)
  // console.log( "Response: " + ajaxRequest.responseText)
  // if AJAX returned a list of markers, add them to the map
  if (ajaxRequest.readyState==4) {
    //use the info here that was returned
    if (ajaxRequest.status==200) {
      plotlist=eval("(" + ajaxRequest.responseText + ")").events;
      console.log(plotlist)
      removeMarkers();
      for (i=0;i<plotlist.length;i++) {
        var plotll = new L.LatLng(plotlist[i].location.lat,plotlist[i].location.lon, true);
        var plotCircle = L.circle(plotll, 500, {color: 'red', fillColor: '#f03', fillOpacity: 0.5})
        // var plotmark = new L.Marker(plotll);
        // plotmark.data=plotlist[i];
        map.addLayer(plotCircle);
        plotCircle.bindPopup("<h3>"+plotlist[i].time+"</h3>"+
          "<p> <b>Lat, Lon: </b>"+plotlist[i].location.lat+","+plotlist[i].location.lon+"</p>"+
          "<p> <b>Altitude: </b>"+plotlist[i].altitude+"</p>"+
          "<p> <b>Size: </b>"+plotlist[i].size+"</p>"+
          "<p> <b>Confidence: </b>"+plotlist[i].confidence+"</p>");
        plotlayers.push(plotCircle);
      }
      console.log('done plotting all the things')
    }
  }
}

function removeMarkers() {
  for (i=0;i<plotlayers.length;i++) {
    map.removeLayer(plotlayers[i]);
  }
  plotlayers=[];
}

function onMapMove(e) { askForPlots(); }

app = {
  initialize: function(){
    initmap()
 }
}
