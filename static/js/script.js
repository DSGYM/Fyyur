window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// // Venue POST Request
// const name = document.getElementById("name");
// const city = document.getElementById("city");
// const state = document.getElementById("state");
// const address = document.getElementById("address");
// const phone = document.getElementById("phone");
// const genres = document.getElementById("genres");
// const facebookLink = document.getElementById("facebook_link");
// const createVenueBtn = document
//   .querySelector(".btn.btn-primary.btn-lg.btn-block")
//   .addEventListener("click", e => {
//     // e.preventDefault();
//     const selected = [];
//     for (var i = 0; i < genres.selectedOptions.length; i++) {
//       selected.push(genres[i].value);
//     }
//     console.log(selected);
//   });
