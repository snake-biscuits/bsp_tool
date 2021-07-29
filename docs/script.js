// scraper.js  Wikipedia -> JSON
// read_database.js  parse DB layout
// write_database.js  save changes
// timeline.js  draw nodes & connections

window.database = {
  "games":
  [
    { "name": "Quake",
      "releases": { "PC (shareware)": "June 22 1996" },
      "links":
      [ "https://en.wikipedia.org/wiki/Quake_(video_game)",
        "https://store.steampowered.com/app/2310/QUAKE/" ]
    },
    { "name": "Quake 2" },
    { "name": "Half-Life" },
    { "name": "Half-Life 2" },
    { "name": "Portal 2" },
  ]
}

fetch("./main.json")
      .then(r => { return r.json() })
      .then(d => console.log(d))
      // .then(data => {window.database = data});

window.timeline = document.getElementById("timeline")


function chronologize(db_list) {
  // get the dates of each node
  // populate a timeline with nodes
}

function generateNode(node_json) {
  // make a node object with links etc.
  // all one dynamic object
  // https://codeburst.io/learn-how-to-create-html-elements-with-plain-javascript-4f1323f96252
}
// ^ calling the above ^
// https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
// https://stackoverflow.com/questions/6456846/how-to-do-an-infinite-scroll-in-plain-javascript

// how are connections drawn?
// maybe 2D canvas background?

function updateDatabase() {
  // identify incomplete entries
  // scrape wiki entries
  // connect to parent groups
  // - list game under dev / engine etc.
  // update citations
  // log text changes
  // use a temp .json before overriding
}

/* web scrapers */
function scrapeWiki(wikipedia_page) {
  // base for wikipedia scrapers
}

function scrapeGame(name) {
  // release dates & platforms
  // dev & publisher
  // technical leads (code & design)
  // links: citations, steam, twitter
  // connections: series, fork etc.
}

function scrapeEngine(name) {
  // release date
  // games
  // connections
  // developer
  // programmers & designers
}

function scrapeDeveloper(name) {
  // acquistions
  // dev careers
  // partnerships
  // games
}


// TODO: CITATIONS IN DATABASE! ALWAYS CREDIT THE SOURCE!
// TODO: track groups
// TODO: hover link preview
//  -- wikipedia entry
//  -- dev twitter bio
//  -- mini steam page
//  -- steam charts
//  -- ratings
// TODO: filter options
// TODO: parallel timelines & columns
// TODO: add landmark, note, node, connection (in html editor)
//  -- live wiki article scraping (do research in editor)
//  -- download changes as .zip (for making a commit / pull request)
// TODO: filters config
// TODO: release platform icons
// TODO: tag/filter buttons
// TODO: search, filter by connections
// TODO: verify database completeness
// TODO: community links
// TODO: generate .zip of changes
//  -- include a batch file to generate a pull request
// TODO: horizonal view
// TODO: group background colour
// TODO: jump to connection
// TODO: connections only view