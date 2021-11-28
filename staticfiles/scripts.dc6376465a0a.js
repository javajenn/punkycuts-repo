let map;

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
  let img = {
      url: "https://cdn-icons-png.flaticon.com/512/3253/3253134.png",
      scaledSize: new google.maps.Size(50,50),
  };
  const blackCoffeeMarker = new google.maps.Marker({
      position: {lat:39.10482143497105,lng:-84.51705276441803},
      map,
      icon: img,
  });
  markers.push(blackCoffeeMarker);
  const pauseCincyMarker = new google.maps.Marker({
      position: {lat:39.133304, lng:-84.509005},
      map,
      icon: img,
  });
  markers.push(pauseCincyMarker);
  const chiChiLLCMarker = new google.maps.Marker({
      position: {lat:39.110392, lng:-84.515408},
      map,
      icon: img,
  })
  markers.push(chiChiLLCMarker);

  const infoWindow = new google.maps.InfoWindow();

  map.data.addListener('click', (event) => {
    const category = event.feature.getProperty('category');
    const name = event.feature.getProperty('name');
    const description = event.feature.getProperty('description');
    const hours = event.feature.getProperty('hours');
    const phone = event.feature.getProperty('phone');
    const content = `
        <h2>${name}</h2><p>${description}</p>
        <p>${category}</p>
        <p>Hours: ${hours}</p>
    `;
    infoWindow.setContent(content);
    infoWindow.open(map);
  })
}