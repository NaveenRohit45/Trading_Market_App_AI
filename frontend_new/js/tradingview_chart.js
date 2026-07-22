new TradingView.widget({
container_id:"tv_chart",
autosize:true,
symbol:"NSE:NIFTY",
interval:"15",
theme:"dark",
style:"1",
locale:"en",
toolbar_bg:"#162033",
hide_top_toolbar:false,
allow_symbol_change:true,
studies:["Volume@tv-basicstudies"],
enabled_features:["study_templates"],
disabled_features:["use_localstorage_for_settings"]
});

/* Change symbol dynamically:
new TradingView.widget({symbol:"NSE:BANKNIFTY", ...});
*/
