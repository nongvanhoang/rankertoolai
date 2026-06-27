// Pinterest Tag — base pixel + conversion events
// Replace REPLACE_TAG_ID with your actual Pinterest Tag ID from:
// Pinterest Ads Manager -> Tools -> Conversions -> Pinterest Tag
!function(e){if(!window.pintrk){window.pintrk=function(){
  window.pintrk.queue.push(Array.prototype.slice.call(arguments))};
  var n=window.pintrk;n.queue=[],n.version="3.0";
  var t=document.createElement("script");t.async=!0,t.src=e;
  var r=document.getElementsByTagName("script")[0];
  r.parentNode.insertBefore(t,r)
}}("https://s.pinimg.com/ct/core.js");

pintrk('load','549770530822');
pintrk('page');

// Fire Lead event on affiliate redirect pages (/go/*)
if(window.location.pathname.indexOf('/go/')===0){
  var slug=window.location.pathname.replace(/^\/go\//,'').replace(/\/$/,'');
  pintrk('track','lead',{lead_type:'affiliate_click',content_ids:[slug],currency:'USD',value:1});
}
