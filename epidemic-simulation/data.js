// State vaccination coverage, percent.
//
// Approximate 2022-2023 CDC figures. MMR is kindergarten two-dose
// coverage from SchoolVaxView. Flu is adult ( >=18 ) seasonal
// coverage from FluVaxView. Both are intentionally point estimates;
// the intent here is pedagogical illustration, not an outbreak
// forecast.
//
// Refresh sources:
//   https://www.cdc.gov/vaccines/imz-managers/coverage/schoolvaxview/
//   https://www.cdc.gov/flu/fluvaxview/
//
// When updating, keep the order alphabetical by name so the map's
// location array stays aligned with the values array without an
// explicit sort step.

const state_coverage = [
  {abb:"AL",name:"Alabama",       mmr:92.5, flu:46.3},
  {abb:"AK",name:"Alaska",        mmr:85.1, flu:42.5},
  {abb:"AZ",name:"Arizona",       mmr:88.8, flu:48.1},
  {abb:"AR",name:"Arkansas",      mmr:92.0, flu:47.0},
  {abb:"CA",name:"California",    mmr:96.2, flu:51.2},
  {abb:"CO",name:"Colorado",      mmr:87.7, flu:50.8},
  {abb:"CT",name:"Connecticut",   mmr:97.2, flu:55.5},
  {abb:"DE",name:"Delaware",      mmr:97.1, flu:54.6},
  {abb:"FL",name:"Florida",       mmr:91.0, flu:42.3},
  {abb:"GA",name:"Georgia",       mmr:93.0, flu:48.7},
  {abb:"HI",name:"Hawaii",        mmr:90.3, flu:49.3},
  {abb:"ID",name:"Idaho",         mmr:87.0, flu:43.0},
  {abb:"IL",name:"Illinois",      mmr:94.9, flu:51.6},
  {abb:"IN",name:"Indiana",       mmr:89.3, flu:50.2},
  {abb:"IA",name:"Iowa",          mmr:91.6, flu:53.2},
  {abb:"KS",name:"Kansas",        mmr:88.1, flu:51.4},
  {abb:"KY",name:"Kentucky",      mmr:88.7, flu:48.5},
  {abb:"LA",name:"Louisiana",     mmr:94.9, flu:45.6},
  {abb:"ME",name:"Maine",         mmr:94.6, flu:53.7},
  {abb:"MD",name:"Maryland",      mmr:96.3, flu:52.9},
  {abb:"MA",name:"Massachusetts", mmr:95.8, flu:56.3},
  {abb:"MI",name:"Michigan",      mmr:89.4, flu:48.1},
  {abb:"MN",name:"Minnesota",     mmr:86.6, flu:52.8},
  {abb:"MS",name:"Mississippi",   mmr:96.7, flu:42.1},
  {abb:"MO",name:"Missouri",      mmr:90.0, flu:47.2},
  {abb:"MT",name:"Montana",       mmr:86.7, flu:48.6},
  {abb:"NE",name:"Nebraska",      mmr:90.3, flu:50.3},
  {abb:"NV",name:"Nevada",        mmr:92.8, flu:40.0},
  {abb:"NH",name:"New Hampshire", mmr:91.5, flu:51.8},
  {abb:"NJ",name:"New Jersey",    mmr:96.5, flu:51.0},
  {abb:"NM",name:"New Mexico",    mmr:94.0, flu:51.1},
  {abb:"NY",name:"New York",      mmr:97.5, flu:54.0},
  {abb:"NC",name:"North Carolina",mmr:93.9, flu:49.4},
  {abb:"ND",name:"North Dakota",  mmr:88.8, flu:53.9},
  {abb:"OH",name:"Ohio",          mmr:88.9, flu:51.2},
  {abb:"OK",name:"Oklahoma",      mmr:89.2, flu:47.1},
  {abb:"OR",name:"Oregon",        mmr:86.8, flu:47.3},
  {abb:"PA",name:"Pennsylvania",  mmr:94.0, flu:51.2},
  {abb:"RI",name:"Rhode Island",  mmr:93.4, flu:58.2},
  {abb:"SC",name:"South Carolina",mmr:94.0, flu:46.5},
  {abb:"SD",name:"South Dakota",  mmr:87.6, flu:53.8},
  {abb:"TN",name:"Tennessee",     mmr:94.4, flu:48.0},
  {abb:"TX",name:"Texas",         mmr:94.7, flu:47.2},
  {abb:"UT",name:"Utah",          mmr:87.8, flu:50.5},
  {abb:"VT",name:"Vermont",       mmr:91.3, flu:52.1},
  {abb:"VA",name:"Virginia",      mmr:92.8, flu:48.3},
  {abb:"WA",name:"Washington",    mmr:85.7, flu:49.4},
  {abb:"WV",name:"West Virginia", mmr:96.8, flu:48.7},
  {abb:"WI",name:"Wisconsin",     mmr:83.7, flu:50.7},
  {abb:"WY",name:"Wyoming",       mmr:88.3, flu:41.0}
];

const state_by_abb = Object.fromEntries(state_coverage.map(s => [s.abb, s]));
