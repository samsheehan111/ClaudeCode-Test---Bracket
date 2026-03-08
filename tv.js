const API_KEY = "21322bdf6abf288ae15aa6a97caf66ae";

const table = document.getElementById("results");

async function loadShows(){

try{

const response = await fetch(
"https://api.themoviedb.org/3/trending/tv/week?api_key=" + API_KEY
);

const data = await response.json();

console.log(data);

if(!data.results){
document.body.innerHTML += "<p>API returned no results</p>";
return;
}

const shows = data.results.sort((a,b)=>b.popularity-a.popularity);

shows.forEach((show,i)=>{

const row=document.createElement("tr");

const poster = show.poster_path
? "https://image.tmdb.org/t/p/w200"+show.poster_path
: "";

row.innerHTML = `
<td>${i+1}</td>
<td><img src="${poster}" width="50"></td>
<td>${show.name}</td>
<td>${show.first_air_date}</td>
<td>${show.origin_country}</td>
<td>${show.vote_average}</td>
<td>${Math.round(show.popularity)}</td>
`;

table.appendChild(row);

});

}catch(err){

document.body.innerHTML += "<p>API ERROR</p>";

console.log(err);

}

}

loadShows();
