import fetch from 'node-fetch';
import fs from 'fs';
import cheerio from 'cheerio';

const BOOKS = [
  // Add your book IDs and SFPL URLs here, e.g.:
  { id: 'o24-01', url: 'https://sfpl.bibliocommons.com/v2/record/S12345' },
  { id: 'o24-02', url: 'https://sfpl.bibliocommons.com/v2/record/S23456' },
  // Continue for all books
];

async function fetchHold(book) {
  try {
    const res = await fetch(book.url);
    const html = await res.text();
    const $ = cheerio.load(html);

    // Only get Libby EBOOK holds
    const libby = $('div[itemtype="ebook"][data-source="Libby"]');
    if (!libby.length) return { status: 'unknown', text: '—' };

    const text = libby.find('.item-status').text().trim();
    return {
      status: text.includes('Available') ? 'available' : 'holds',
      text,
    };
  } catch (e) {
    return { status: 'unknown', text: '—' };
  }
}

(async () => {
  const books = {};
  for (const b of BOOKS) {
    books[b.id] = await fetchHold(b);
  }
  fs.writeFileSync('holds.json', JSON.stringify({
    updated: new Date().toISOString(),
    books
  }, null, 2));
})();
