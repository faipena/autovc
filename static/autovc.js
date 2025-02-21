import {io} from "/static/socket.io/4.8.1/socket.io.esm.min.js"; 

const socket = io("127.0.0.1:18889");
const MONITOR_DEVICE = "default";
const DEBUG = true;
let log = DEBUG ? ((...what) => console.log("[AUTOVC]", ...what)) : ((...what) => { });

socket.on("vc start", () => {
  log("vc start");
  changeState(true);
});

socket.on("vc stop", () => {
  log("vc stop");
  changeState(false);
});

socket.on("vc monitor toggle", () => {
  log("vc monitor toggle");
  const monitorSelect = document.querySelectorAll("div.config-sub-area-control-field select")[6];
  if(monitorSelect.value === "none") {
    monitorSelect.value = MONITOR_DEVICE;
  } else {
    monitorSelect.value = "none";
  }
});


function changeState(started) {
  const buttonsParent = document.querySelector("div.character-area-control-buttons");
  if (started) {
    buttonsParent.children[0].click();
  } else {
    buttonsParent.children[1].click();
  }
}