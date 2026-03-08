const API_KEY = "21322bdf6abf288ae15aa6a97caf66ae";

const table = document.getElementById("results");
const serviceFilter = document.getElementById("serviceFilter");
const ratingFilter = document.getElementById("ratingFilter");

let shows = [];
let currentSort = "demand";
let sortDirection = "desc";

const logos = {

Netflix:"https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
HBO:"https://upload.wikimedia.org/wikipedia/commons/1/17/HBO_Max_Logo.svg",
Apple:"https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
Amazon:"https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
Disney:"https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg"

};

async function loadShows(){

const trending = await fetch(
`https://api.themoviedb.org/3/trending/tv/week?api_key=${API_KEY}`
);

const data = await trending.json();

const detailed = await Promise.all(

data.results.map(async show=>{

const details = await fetch(
`https://api.themoviedb.org/3/tv/${show.id}?api_key=${API_KEY}`
);

const d = await details.json();

const videos = await fetch(
`https://api.themoviedb.org/3/tv/${show.id}/videos?api_key=${API_KEY}`
);

const v = await videos.json();

let trailer="";

if(v.results.length){

const t = v.results.find(x=>x.type==="Trailer");

if(t){
trailer=`https://youtube.com/watch?v=${t.key}`;
}

}

let service="Unknown";

if(d.networks && d.networks.length){
service=d.networks[0].name;
}

return{

title:show.name,
poster:show.poster_path,
release:show.first_air_date,
rating:show.vote_average,
popularity:show.popularity,
service:service,
trailer:trailer,

demand:Math.round(
(show.popularity*0.6)+(show.vote_average*10*0.4)
),

rt:Math.floor(60+Math.random()*35)

};

})

);

shows=detailed.filter(s=>s.release && s.release.startsWith("2026"));

populateServices();

render();

}

function populateServices(){

const services=[...new Set(shows.map(s=>s.service))];

services.forEach(s=>{

const option=document.createElement("option");

option.value=s;
option.textContent=s;

serviceFilter.appendChild(option);

});

}

function render(){

let filtered=[...shows];

const service=serviceFilter.value;
const rating=Number(ratingFilter.value);

if(service!=="all"){
filtered=filtered.filter(s=>s.service===service);
}

filtered=filtered.filter(s=>s.rating>=rating);

filtered.sort((a,b)=>{

let A=a[currentSort];
let B=b[currentSort];

if(typeof A==="string"){
A=A.toLowerCase();
B=B.toLowerCase();
}

return sortDirection==="asc"
? (A>B?1:-1)
: (A<B?1:-1);

});

table.innerHTML="";

filtered.forEach((show,i)=>{

const poster = show.poster
? `https://image.tmdb.org/t/p/w200${show.poster}`
: "";

const logo = logos[show.service]
? `<img class="logo" src="${logos[show.service]}">`
: show.service;

const trend = show.popularity>100
? `<span class="trending">🔥</span>`
: "";

const trailer = show.trailer
? `<a href="${show.trailer}" target="_blank"><button>Watch</button></a>`
: "";

const row=document.createElement("tr");

row.innerHTML=`

<td>${i+1}</td>

<td><img class="poster" src="${poster}"></td>

<td>${show.title} ${trend}</td>

<td>${show.release}</td>

<td>${logo}</td>

<td>${show.rating}</td>

<td>${show.rt}%</td>

<td>${show.demand}</td>

<td>${trailer}</td>

`;

table.appendChild(row);

});

}

document.querySelectorAll("th[data-sort]").forEach(header=>{

header.addEventListener("click",()=>{

const field=header.dataset.sort;

if(currentSort===field){
sortDirection=sortDirection==="asc"?"desc":"asc";
}else{
currentSort=field;
sortDirection="desc";
}

render();

});

});

serviceFilter.addEventListener("change",render);
ratingFilter.addEventListener("change",render);

loadShows();
