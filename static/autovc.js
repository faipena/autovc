import {io} from "/static/socket.io/4.8.1/socket.io.esm.min.js"; 

const socket = io("127.0.0.1:18889");

const DEBUG = true;
let log = DEBUG ? ((...what) => console.log("[AUTOVC]", ...what)) : ((...what) => { });

socket.on("vc start", () => {
  log("on vc start!");
  changeState(true);
});

socket.on("vc stop", () => {
  log("on vc stop!");
  changeState(false);
});


function changeState(started) {
  const buttonsParent = document.querySelector("div.character-area-control-buttons");
  if (!buttonsParent || buttonsParent.childElementCount < 2) {
    return;
  }
  const startButton = buttonsParent.children[0];
  const stopButton = buttonsParent.children[1];
  if (!(startButton && stopButton)) {
    return;
  }
  if (started) {
    startButton.click();
  } else {
    stopButton.click();
  }
}