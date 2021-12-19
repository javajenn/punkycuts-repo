var map;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 39.123880, lng: -84.508303},
    zoom: 13,
  });

//   new google.maps.Marker({
//     position: {lat:39.10482143497105,lng:-84.51705276441803},
//     map,
//     title: 'My favorite place for coffee!'
//   });
  let markers = [];
  debugger;
  let img = {
      url: "https://cdn-icons-png.flaticon.com/512/3253/3253134.png",
      scaledSize: new google.maps.Size(50,50),
  };
  const blackCoffeeInfo = new google.maps.InfoWindow({
      content: "<div class='info'><h2>blaCk Coffee lounge</h2><p>Black-owned local coffee shop with delicious chai lattes!</p></div>",
  });
  const blackCoffeeMarker = new google.maps.Marker({
      position: {lat:39.10482143497105,lng:-84.51705276441803},
      map,
      icon: img,
  });
  markers.push(blackCoffeeMarker);
  blackCoffeeMarker.addListener('click', ()=>{
      blackCoffeeInfo.open({
        anchor: blackCoffeeMarker,
        map,
        shouldFocus: false,
      });
  });
  const pauseCincyInfo = new google.maps.InfoWindow({
    content: "<div class='info'><h2>Pause Cincy</h2><p>Everything wellness! Plants, crystals, juices, and more.</p></div>",
  });
  const pauseCincyMarker = new google.maps.Marker({
      position: {lat:39.133304, lng:-84.509005},
      map,
      icon: img,
  });
  markers.push(pauseCincyMarker);
  pauseCincyMarker.addListener('click', ()=>{
    pauseCincyInfo.open({
      anchor: pauseCincyMarker,
      map,
      shouldFocus: false,
    });
  });
  const chiChiLLCInfo = new google.maps.InfoWindow({
    content: "<div class='info'><h2>Chi Chi LLC</h2><p>Women's owned small local business!</p></div>",
  });
  const chiChiLLCMarker = new google.maps.Marker({
      position: {lat:39.110392, lng:-84.515408},
      map,
      icon: img,
  })
  markers.push(chiChiLLCMarker);
  chiChiLLCMarker.addListener('click', ()=>{
    chiChiLLCInfo.open({
      anchor: chiChiLLCMarker,
      map,
      shouldFocus: false,
    })
  })
}

