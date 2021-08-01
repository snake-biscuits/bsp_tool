// wiki_trawl.js      WikiMedia API -> JSON
// read_database.js   parse DB layout
// write_database.js  save changes
// timeline.js        draw nodes & connections

// https://developer.valvesoftware.com/wiki/Quake_Engine_Hierarchy
// ^ extend this and make it interactive!
// https://en.wikipedia.org/wiki/Quake_(video_game)#/media/File:Quake_-_family_tree.svg
// ^ more linear, but out of date!
// https://en.wikipedia.org/wiki/Quake_(video_game)#/media/File:Quake_-_family_tree_2.svg
// ^ clearer, but goes backwards and misses Titanfall & CoD

window.database = {
  "games":
  [
    { "name": "Quake",
      "releases": {"PC (shareware)": "June 22 1996"},
      "links":
      [ "https://en.wikipedia.org/wiki/Quake_(video_game)",
        "https://store.steampowered.com/app/2310/QUAKE/" ],
      "citations": {"releases['PC (shareware)']": "wikipedia"}
    },
    { "name": "Quake II",
      "links": ["https://en.wikipedia.org/wiki/Quake_II"]
    }
  ]
}

fetch("https://snake-biscuits.github.io/bsp_tool/main.json")
      .then(r => { return r.json() })
      .then(d => console.log(d))
      // .then(data => {window.database = data})

window.timeline = document.getElementById("timeline")


function chronologiesGames() {
  for (game in window.database.games) {
    release_year = 2021
    for (platform in game.releases) {
        year = Number(platform.substr(-4, -1))
        if (year < release_year) {
            release_year = year;
        }
    }
  }
  // get the dates of each node
  // populate a timeline with nodes
}

function generateNode(node_json) {
  // make a node object with links etc.
  // all one dynamic object
  // https://codeburst.io/learn-how-to-create-html-elements-with-plain-javascript-4f1323f96252
  // insert table row
  // td year, td <div class="node"> [many nodes]
}
// ^ calling the above ^
// https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
// https://stackoverflow.com/questions/6456846/how-to-do-an-infinite-scroll-in-plain-javascript

// how are connections drawn?
// maybe 2D canvas background?


/* database ops */
function updateDatabase() {
  // identify incomplete entries
  // trawl wikipedia
  // make connections
  // - list game under dev / engine etc.
  // update citations
  // log a diff
  // use a temp .json, don't overwrite the old one!
}

/* data trawling */
function trawlWiki(wikipedia_page) {
  // https://www.mediawiki.org/wiki/API:Etiquette
}

function processGamePage(wiki_page) {
  // release dates & platforms
  // dev & publisher
  // technical leads (code & design)
  // links: citations, steam, twitter
  // connections: series, fork etc.
}

function procressEnginePage(wiki_page) {
  // release date
  // games
  // connections
  // developer
  // programmers & designers
}

function processDeveloperPage(name) {
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
