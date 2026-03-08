const shows = [
  { title: "Shadow Protocol", releaseDate: "2026-01-04", month: "January", platforms: ["Netflix"], rtCritic: 82, rtAudience: 79, imdb: 7.6, tmdbPopularity: 86, votes: 18200 },
  { title: "Neon District", releaseDate: "2026-01-08", month: "January", platforms: ["Max"], rtCritic: 75, rtAudience: 72, imdb: 7.1, tmdbPopularity: 64, votes: 9300 },
  { title: "Evergreen Fire", releaseDate: "2026-01-10", month: "January", platforms: ["Apple TV+"], rtCritic: 91, rtAudience: 88, imdb: 8.3, tmdbPopularity: 73, votes: 12400 },
  { title: "Last Run to Phoenix", releaseDate: "2026-01-12", month: "January", platforms: ["Prime Video"], rtCritic: 68, rtAudience: 66, imdb: 6.8, tmdbPopularity: 58, votes: 6900 },
  { title: "Harborline", releaseDate: "2026-01-16", month: "January", platforms: ["Hulu"], rtCritic: 84, rtAudience: 77, imdb: 7.5, tmdbPopularity: 61, votes: 8400 },
  { title: "Alloy Hearts", releaseDate: "2026-01-22", month: "January", platforms: ["Disney+"], rtCritic: 63, rtAudience: 61, imdb: 6.2, tmdbPopularity: 52, votes: 5100 },
  { title: "Crimson Ledger", releaseDate: "2026-01-28", month: "January", platforms: ["Peacock"], rtCritic: 88, rtAudience: 85, imdb: 8.0, tmdbPopularity: 70, votes: 10500 },
  { title: "The Sixth Orbit", releaseDate: "2026-02-02", month: "February", platforms: ["Netflix"], rtCritic: 93, rtAudience: 89, imdb: 8.4, tmdbPopularity: 94, votes: 24500 },
  { title: "Paper Monarch", releaseDate: "2026-02-05", month: "February", platforms: ["Prime Video"], rtCritic: 74, rtAudience: 70, imdb: 7.0, tmdbPopularity: 62, votes: 7600 },
  { title: "Rose & Iron", releaseDate: "2026-02-07", month: "February", platforms: ["Max"], rtCritic: 86, rtAudience: 80, imdb: 7.8, tmdbPopularity: 69, votes: 9800 },
  { title: "The Quiet Coast", releaseDate: "2026-02-11", month: "February", platforms: ["Hulu"], rtCritic: 79, rtAudience: 76, imdb: 7.3, tmdbPopularity: 57, votes: 6600 },
  { title: "Beneath Saturn", releaseDate: "2026-02-14", month: "February", platforms: ["Apple TV+"], rtCritic: 90, rtAudience: 87, imdb: 8.2, tmdbPopularity: 77, votes: 13300 },
  { title: "Rookie Saints", releaseDate: "2026-02-18", month: "February", platforms: ["Disney+"], rtCritic: 71, rtAudience: 68, imdb: 6.9, tmdbPopularity: 60, votes: 7400 },
  { title: "Frostwire", releaseDate: "2026-02-21", month: "February", platforms: ["Paramount+"], rtCritic: 66, rtAudience: 62, imdb: 6.4, tmdbPopularity: 49, votes: 4300 },
  { title: "Cinder Lake", releaseDate: "2026-02-25", month: "February", platforms: ["Peacock"], rtCritic: 85, rtAudience: 82, imdb: 7.9, tmdbPopularity: 68, votes: 8800 }
];

const monthFilter = document.getElementById("monthFilter");
const platformFilter = document.getElementById("platformFilter");
const popularityFilter = document.getElementById("popularityFilter");
const popularityValue = document.getElementById("popularityValue");
const qualityFilter = document.getElementById("qualityFilter");
const resultsBody = document.getElementById("resultsBody");
const countLabel = document.getElementById("countLabel");
const rangeLabel = document.getElementById("rangeLabel");

function popularityScore(show) {
  const score =
    show.tmdbPopularity * 0.35 +
    show.imdb * 10 * 0.25 +
    show.rtAudience * 0.2 +
    show.rtCritic * 0.15 +
    Math.log10(show.votes + 1) * 10 * 0.05;
  return Math.max(0, Math.min(100, Number(score.toFixed(1))));
}

function setPlatformOptions() {
  const allPlatforms = Array.from(new Set(shows.flatMap((show) => show.platforms))).sort();
  for (const platform of allPlatforms) {
    const option = document.createElement("option");
    option.value = platform;
    option.textContent = platform;
    platformFilter.appendChild(option);
  }
}

function passesQuality(show) {
  return show.imdb >= 6.5 && show.rtAudience >= 65;
}

function render() {
  popularityValue.textContent = popularityFilter.value;

  const filtered = shows
    .map((show) => ({ ...show, popularity: popularityScore(show) }))
    .filter((show) => monthFilter.value === "all" || show.month === monthFilter.value)
    .filter((show) => platformFilter.value === "all" || show.platforms.includes(platformFilter.value))
    .filter((show) => show.popularity >= Number(popularityFilter.value))
    .filter((show) => !qualityFilter.checked || passesQuality(show))
    .sort((a, b) => b.popularity - a.popularity);

  resultsBody.innerHTML = "";

  filtered.forEach((show, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${index + 1}</td>
      <td><strong>${show.title}</strong></td>
      <td>${show.releaseDate}</td>
      <td>${show.platforms.map((platform) => `<span class="badge">${platform}</span>`).join("")}</td>
      <td>${show.rtCritic}%</td>
      <td>${show.rtAudience}%</td>
      <td>${show.imdb.toFixed(1)}</td>
      <td class="pop">${show.popularity}</td>
    `;
    resultsBody.appendChild(row);
  });

  countLabel.textContent = `${filtered.length} show${filtered.length === 1 ? "" : "s"} displayed`;
  rangeLabel.textContent = "Date range: 2026-01-01 to 2026-02-28";
}

setPlatformOptions();
render();

[monthFilter, platformFilter, popularityFilter, qualityFilter].forEach((element) => {
  element.addEventListener("input", render);
});
