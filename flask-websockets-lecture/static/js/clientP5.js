let flowers = [];
let state = "waiting";
let clientSocket =null; //put out here

window.onload = function () {
  console.log("loaded");
  let uName = "";
  let io_client = io(); //js library
  clientSocket = io_client.connect("http://localhost:5000");
  console.log(clientSocket);
  document.querySelector("#uButton").addEventListener("click", function () {
    uName = document.querySelector("#uName").value;
    console.log(uName);
    //inital handshake send to server
    clientSocket.emit("join", uName); // Notify server of new user
  });

  //receive notice from server :)
  clientSocket.on("join-complete", function (data) {
    console.log("server registered my join");
    //hide the username input
    document.querySelector(".username-container").style.display = "none";
    document.querySelector("#p5Test").style.display = "block";
    //for p5
    state = "active";
  });
};
/*************************p5*********************************** */

let clientScopeFlowerCol = {};
function setup() {
  let canvas = createCanvas(800,600); // Create your canvas
  canvas.parent("p5Test"); // Attach the canvas to the div with id 'p5Container'
  background(0);
  textSize(22);
  clientScopeFlowerCol.outerCol = color(random(255), random(255), random(255));
  clientScopeFlowerCol.innerCol = color(random(255), random(255), random(255));
  clientScopeFlowerCol.scalar = random(10,60);
}
function draw() {
  background(0);

  if (state === "active") {
    for (let i = 0; i < flowers.length; i++) {
      flowers[i].drawFlower();
      flowers[i].scaleFlower();
    }
  }
}
function mousePressed() {
  if (state === "active") {
    console.log(flowers.length);
    let tempFlower = new Flower(
        mouseX,
        mouseY,
        clientScopeFlowerCol.outerCol,
        clientScopeFlowerCol.innerCol,
        clientScopeFlowerCol.scalar
      )
    flowers.push(tempFlower);
    //new
    clientSocket.emit("newFlower", tempFlower); // Notify server of new flower
  }

  clientSocket.on("flowerFromServer", function (flowerData) {
    let tempFlower = new Flower(
        flowerData.x,
        flowerData.y,
        flowerData.o_color.levels,
        flowerData.i_color.levels,
        flowerData.scalar
      )
     flowers.push(tempFlower);
})
  
}