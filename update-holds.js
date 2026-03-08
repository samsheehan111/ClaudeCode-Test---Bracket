const fs = require("fs");
const fetch = require("node-fetch");
const cheerio = require("cheerio");

const BOOKS = JSON.parse(fs.readFileSync("books.json"));
