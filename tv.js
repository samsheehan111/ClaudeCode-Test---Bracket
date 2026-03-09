const TMDB_KEY  = "21322bdf6abf288ae15aa6a97caf66ae";
const OMDB_KEY  = "679ba5a1";

const table = document.getElementById("results");
const serviceFilter = document.getElementById("serviceFilter");
const ratingFilter  = document.getElementById("ratingFilter");

let shows       = [];
let currentSort = "demand";
let sortDesc    = true;

const logos = {
  Netflix:"https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
  HBO:"https://upload.wikimedia.org/wikipedia/commons/1/17/HBO_Max_Logo.svg",
  Apple:"https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
  Amazon:"https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
  Disney:"https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg"
};

async function fetchAll2026Shows() {
  let all = [];
  for (let page = 1; page <= 10; page++) {
    const res = await fetch(
      `https://api.themoviedb.org/3/discover/tv?api_key=${TMDB_KEY}&first_air_date_year=2026&sort_by=popularity.desc&page=${page}`
    );
    const data = await res.json();
    all = all.concat(data.results);
  }
  return all;
}

async function fetchOMDbScores(title, year) {
  const res = await fetch(
    `https://www.omdbapi.com/?apikey=${OMDB_KEY}&t=${encodeURIComponent(title)}&y=${year}&tomatoes=true`
  );
  const data = await res.json();
  return {
    imdb: data.imdbRating || "-",
    rtCritic: data.Ratings?.find(r => r.Source==="Rotten Tomatoes")?.Value || "-"
  };
}

async function loadShows() {
  const rawShows = await fetchAll2026Shows();

  const detailed = await Promise.all(
    rawShows.map(async show => {
      const videos  = await fetch(
        `https://api.themoviedb.org/3/tv/${show.id}/videos?api_key=${TMDB_KEY}`
      );
      const v = await videos.json();
      const trailerResult = v.results.find(x => x.type === "Trailer");
      const trailer = trailerResult
        ? `https://www.youtube.com/watch?v=${trailerResult.key}`
        : "";

      const omdb = await fetchOMDbScores(show.name, show.first_air_date?.slice(0,4));

      let service = "Unknown";
      if (show.networks && show.networks.length) {
        service = show.networks[0].name;
      }

      return {
        title: show.name,
        poster: show.poster_path,
        release: show.first_air_date,
        service: service,
        imdb: omdb.imdb,
        rtCritic: omdb.rtCritic,
        trailer: trailer,
        demand: Math.round(
          (show.popularity * 0.7) + ((parseFloat(omdb.imdb) || 0) * 10 * 0.3)
        )
      };
    })
  );

  shows = detailed;
  populateServices();
  render();
}

function populateServices() {
  const list = [...new Set(shows.map(s => s.service))];
  list.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    serviceFilter.appendChild(opt);
  });
}

function render() {
  let filtered = [...shows];
  if (serviceFilter.value !== "all") {
    filtered = filtered.filter(s => s.service === serviceFilter.value);
  }
  const minRating = Number(ratingFilter.value);
  filtered = filtered.filter(s => parseFloat(s.imdb) >= minRating);

  filtered.sort((a,b) => {
    let A = a[currentSort], B = b[currentSort];
    if (typeof A === "string") { A = A.toLowerCase(); B = B.toLowerCase(); }
    return sortDesc
      ? (A < B ? 1 : -1)
      : (A > B ? 1 : -1);
  });

  table.innerHTML = "";
  filtered.forEach((show,i) => {
    const poster = show.poster
      ? `https://image.tmdb.org/t/p/w200${show.poster}`
      : "";
    const logo = logos[show.service]
      ? `<img class="logo" src="${logos[show.service]}">`
      : show.service;
    const trailerButton = show.trailer
      ? `<a href="${show.trailer}" target="_blank"><button>Trailer</button></a>`
      : "";

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${i+1}</td>
      <td><img class="poster" src="${poster}"></td>
      <td>${show.title}</td>
      <td>${show.release}</td>
      <td>${logo}</td>
      <td>${show.imdb}</td>
      <td>${show.rtCritic}</td>
      <td>${show.demand}</td>
      <td>${trailerButton}</td>
    `;
    table.appendChild(row);
  });
}

document.querySelectorAll("th[data-sort]").forEach(header => {
  header.addEventListener("click", () => {
    const field = header.dataset.sort;
    if (currentSort === field) sortDesc = !sortDesc;
    else { currentSort = field; sortDesc = true; }
    render();
  });
});

serviceFilter.addEventListener("change", render);
ratingFilter.addEventListener("change", render);

loadShows();
