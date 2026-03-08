const API_KEY = "21322bdf6abf288ae15aa6a97caf66ae";

const table = document.getElementById("results");
const serviceFilter = document.getElementById("serviceFilter");

let shows = [];
let currentSort = "popularity";
let sortDirection = "desc";

async function loadShows(){

const trending = await fetch(
`https://api.themoviedb.org/3/trending/tv/week?api_key=${API_KEY}`
);

const data = await trending.json();

const detailedShows = await Promise.all(

data.results.map(async show => {

const details = await fetch(
`https://api.themoviedb.org/3/tv/${show.id}?api_key=${API_KEY}`
);

const d = await details.json();

let service = "Unknown";

if(d.networks && d.networks.length){
service = d.networks[0].name;
}

return {

title: show.name,
poster: show.poster_path,
release: show.first_air_date,
rating: show.vote_average,
popularity: Math.round(show.popularity),
service: service

};

})

);

shows = detailedShows.filter(show =>
show.release && show.release.startsWith("2026")
);

populateServices();

render();

}

function populateServices(){

const services = [...new Set(shows.map(s => s.service))];

services.forEach(service => {

const option = document.createElement("option");
option.value = service;
option.textContent = service;

serviceFilter.appendChild(option);

});

}

function render(){

let filtered = [...shows];

const selectedService = serviceFilter.value;

if(selectedService !== "all"){
filtered = filtered.filter(s => s.service === selectedService);
}

filtered.sort((a,b)=>{

let valA = a[currentSort];
let valB = b[currentSort];

if(currentSort === "title" || currentSort === "service"){
valA = valA.toLowerCase();
valB = valB.toLowerCase();
}

if(sortDirection === "asc"){
return valA > valB ? 1 : -1;
}else{
return valA < valB ? 1 : -1;
}

});

table.innerHTML = "";

filtered.forEach((show,index)=>{

const row = document.createElement("tr");

const poster = show.poster
? `https://image.tmdb.org/t/p/w200${show.poster}`
: "";

row.innerHTML = `

<td>${index+1}</td>

<td>
<img class="poster" src="${poster}">
</td>

<td>${show.title}</td>

<td>${show.release}</td>

<td>${show.service}</td>

<td>${show.rating}</td>

<td>${show.popularity}</td>

`;

table.appendChild(row);

});

}

document.querySelectorAll("th[data-sort]").forEach(header => {

header.addEventListener("click", () => {

const field = header.dataset.sort;

if(currentSort === field){
sortDirection = sortDirection === "asc" ? "desc" : "asc";
}else{
currentSort = field;
sortDirection = "desc";
}

render();

});

});

serviceFilter.addEventListener("change", render);

loadShows();
