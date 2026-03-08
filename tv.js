const API_KEY = "PASTE_API_KEY_HERE";

const table = document.getElementById("results");

async function loadShows(){

const response = await fetch(
`https://api.themoviedb.org/3/trending/tv/week?api_key=${API_KEY}`
);

const data = await response.json();

const shows = data.results.sort((a,b)=>b.popularity-a.popularity);

table.innerHTML="";

shows.forEach((show,index)=>{

let poster="";

if(show.poster_path){
poster=`https://image.tmdb.org/t/p/w200${show.poster_path}`;
}

const row=document.createElement("tr");

row.innerHTML=`

<td>${index+1}</td>

<td>
<img class="poster" src="${poster}">
</td>

<td>${show.name}</td>

<td>${show.first_air_date}</td>

<td>${show.origin_country}</td>

<td>${show.vote_average}</td>

<td>${Math.round(show.popularity)}</td>

`;

table.appendChild(row);

});

}

loadShows();
