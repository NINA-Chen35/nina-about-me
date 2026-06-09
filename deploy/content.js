// Nina Content Data
// 此檔案由管理後台 admin.html 自動生成，請勿直接手動修改
window.NINA_DATA = {
  "groupBuy": {
    "pinnedBanner": {
      "enabled": false,
      "tags": [],
      "title": "",
      "subtitle": "",
      "image": "",
      "link": ""
    },
    "schedules": []
  },
  "github": {
    "owner": "NINA-Chen35",
    "repo": "nina-about-me",
    "branch": "main",
    "path": "deploy/content.js",
    "siteurl": "https://nina-about-me.vercel.app"
  }
};

// 頭像連點 5 下進入後台
(function(){
  function init(){
    var el=document.getElementById('topAvatar');
    if(!el)return;
    var clicks=0,timer;
    function tap(e){e.preventDefault();clicks++;clearTimeout(timer);if(clicks>=5){clicks=0;window.location.href='admin.html';}else{timer=setTimeout(function(){clicks=0;},2000);}}
    el.addEventListener('touchend',tap,{passive:false});
    el.addEventListener('click',tap);
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}
})();
