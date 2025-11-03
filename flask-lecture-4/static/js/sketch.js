/**
 * Create the canvas
 */

let paddle = null;
let ball = null;
let bricks = [];
let score = 0;
const BRICK_W = 40;
const BRICK_H = 20;
const NUM_COLS = 600 / BRICK_W;
const NUM_ROWS = 200 / BRICK_H;
let keyCode = 0;
let gameState = "start"; // state of the application

//FOR LATER
let label = `Type your Name and then Press ENTER: \n `;
let nameToSave =""
let oldScore =""

function preload() {}

function setup() {
  let canvas = createCanvas(600, 450); // Create your canvas
  canvas.parent("p5Container"); // Attach the canvas to the div with id 'p5Container'
  background(220); // Set a background color for the canvas
  textSize(22);

  let brick_cols = [
    "#E87F78",
    "#E8B778",
    "#E1E878",
    "#78e4e8ff",
    "#78e896ff",
    "#789be8ff",
  ];

  //add bricks to array
  for (let i = 0; i < NUM_COLS; i++) {
    for (let j = 0; j < NUM_ROWS; j++) {
      bricks.push(
        new Brick(
          i * BRICK_W,
          j * BRICK_H,
          BRICK_W,
          BRICK_H,
          brick_cols[floor(random(0, brick_cols.length))]
        )
      );
    }
  }
  //make a ball
  ball = new Ball(width / 2, height / 2, 15, 15, "#eafb89ff", "#f313ddff");
  //make a paddle
  paddle = new Paddle(width / 2, height - 12, 60, 10, "#FFFFFF");
}



function draw() {
  //default
  background("#333333");

    /*** gameState - save the name */
   /*** gameState - after save name save the score */
  if(gameState === "saveData"){
     displayInfo(`Saving ${nameToSave}'s score of ${score}...`, width / 2, height / 2 + 20);
     sendData({ id:nameToSave, score: score });
 }

  /*** once received notification from server that data is saved we can end */
  if (gameState === "end") {
    //if we got data back - then this should be a new score
    if(oldScore!=""){
       displayInfo(`${nameToSave}'s OLD score was ${oldScore}.`, width / 2, height / 2-20);
       displayInfo(`Now Saved ${nameToSave}'s score of ${score}.`, width / 2, height / 2 + 20);
       }

    else {
       displayInfo(`Saved ${nameToSave}'s score of ${score}.`, width / 2, height / 2 + 20);

    }
   
    displayInfo(`BYE!\n`, width / 2, height / 2 + 60);
  }
  /*** gameState is paused : user lost but can choose to quit or try again */
  if (gameState === "pause") {
    displayBricks();
    ball.display();
    paddle.display();
    displayInfo(
      `Lost!\n 
      Press the Space Bar to try again.\n
      Press Q to quit.\n`,
      width / 2,
      height / 2 + 20
    );
    //check if space or q
    if (keyIsPressed) {
      //play again
      if (keyCode === 32) {
        gameState = "play";
        score =0;
        oldScore =""
        document.querySelector("#p5Score").innerHTML = `SCORE: ${score}`
        ball.reset();
      }
      //end
      if (keyCode === 81) {
        gameState = "saveName";
      }
    }
  }

  /* gameState is in play mode */
  if (gameState === "play") {
    //display bricks in the brick array
    displayBricks();
    //display the ball
    ball.display();
    //update the ball and check collision with sideas and bottom,top
    ball.update();
    //display the paddle
    paddle.display();
    //collision between paddle and ball?
    paddle.checkCollisionWithBall(ball);
    //collision between ball and bricks?
    ball.checkCollWithBricks(bricks);

    //check for key press
    if (keyIsPressed) {
      //right
      if (keyCode === 39) {
        paddle.moveRight();
      }
      //left
      if (keyCode === 37) {
        paddle.moveLeft();
      }
    }
  }
   /*** gameState - start */
  if (gameState === "start") {
    displayInfo("PRESS space bar to START", width / 2, height / 2);
    if(keyIsPressed){
      if (keyCode === 32){
        gameState = "play"
      }
    }


  }
}//end draw
/*******HELPER FUNCTIONS  ******/
//for displaying text
function displayInfo(infoText, x, y) {
  push();
  fill("#ffffff");
  textAlign(CENTER);
  text(infoText.toUpperCase(), x, y);
  pop();
}

//for displaying bricks
function displayBricks() {
  for (let i = 0; i < bricks.length; i++) {
    bricks[i].display();
  }
}
//check key press
function keyPressed(e) {
  // console.log("key");
  console.log(e);
  keyCode = e.keyCode;

  // save user name
  if (gameState === "saveName") {
    //check if is lower /uppercase letter
    if (
      (e.keyCode >= 65 && e.keyCode <= 90) ||
      (e.keyCode >= 97 && e.keyCode <= 122)
    ){
         nameToSave += key;

    }
     //user finished
    else if(e.keyCode ===13){
      gameState = "saveData"
    }
   
  }
  
}

/* function to send data to server */
async function sendData(params) {
  const queryParams = new URLSearchParams(params).toString();
  console.log(queryParams);
  //build the url -end point
  const url = `/getDataFromP5?${queryParams}`;
  try {
    let res = await fetch(url);
    let resJSON = await res.json();
    console.log(resJSON);
    gameState = 'end'
     if(resJSON.score!==undefined){
     oldScore = resJSON.score
    }
   
  } catch (err) {
    console.log(err);
  }
}