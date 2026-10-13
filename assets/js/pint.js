// Pinterest Tag — base pixel + conversion events
// Tag ID from Pinterest Ads Manager -> Conversions -> Tag manager (ad account 549770530822).
// Don't put the ad account ID here: Pinterest warns "configured with an advertiser ID".
!function(e){if(!window.pintrk){window.pintrk=function(){
  window.pintrk.queue.push(Array.prototype.slice.call(arguments))};
  var n=window.pintrk;n.queue=[],n.version="3.0";
  var t=document.createElement("script");t.async=!0,t.src=e;
  var r=document.getElementsByTagName("script")[0];
  r.parentNode.insertBefore(t,r)
}}("https://s.pinimg.com/ct/core.js");

pintrk('load','2612617794940');
pintrk('page');

// Fire Lead event on affiliate redirect pages (/go/*)
if(window.location.pathname.indexOf('/go/')===0){
  var slug=window.location.pathname.replace(/^\/go\//,'').replace(/\/$/,'');
  pintrk('track','lead',{lead_type:'affiliate_click',content_ids:[slug],currency:'USD',value:1});
}
