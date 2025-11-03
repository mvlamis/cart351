let fireworks = [];

let donutImages = [];


function setup() {
  createCanvas(800, 600);
  donutImages = [
    loadImage('static/images/donut_a.png'),
    loadImage('static/images/donut_b.png'),
    loadImage('static/images/donut_c.png'),
    loadImage('static/images/donut_d.png'),
    loadImage('static/images/donut_e.png'),
    loadImage('static/images/donut_f.png')
];

}

function draw() {
  background(0);
    updateFireworks();
    displayFireworks();
    console.log(fireworks);
    if (showProgress) {
        drawProgressCircle();
    }

}

function createFirework(x, y, size, opacity, imageIndex) {
    let firework = {
        x: x,
        y: y,
        size: size,
        opacity: opacity,
        imageIndex: imageIndex
    };
    fireworks.push(firework);

    sendData(firework);
    
    
}

function updateFireworks() {
    for (let i = fireworks.length - 1; i >= 0; i--) {
        let firework = fireworks[i];
        firework.size += 1;
        firework.opacity -= 5;
        
    }
}

function displayFireworks() {
    for (let firework of fireworks) {
        push();
        translate(firework.x, firework.y);
        tint(255, firework.opacity);
        imageMode(CENTER);
        image(donutImages[firework.imageIndex], 0, 0, firework.size, firework.size);
        pop();


    }
}

// function mousePressed() {
//     createFirework(mouseX, mouseY, random(20, 100), 255);
// }


function drawProgressCircle() {
    let holdDuration = millis() - holdStartTime;
    let progress = map(holdDuration, 0, 2000, 0, 1);
    progress = constrain(progress, 0, 1);

    push()
    noFill();
    stroke(255);
    strokeWeight(4);
    ellipse(mouseX, mouseY, progress * 100);
    pop();

}

// firework size controlled by mouse hold duration
let holdStartTime = 0;
let showProgress = false;

function mousePressed() {
    holdStartTime = millis();
    showProgress = true;
}

function mouseReleased() {
    let holdDuration = millis() - holdStartTime;
    let size = map(holdDuration, 0, 2000, 20, 200);
    size = constrain(size, 20, 300);
    createFirework(mouseX, mouseY, size, 255, floor(random(0, donutImages.length)));
    holdStartTime = 0;
    showProgress = false;
    
}

async function sendData(firework) {
    console.log(firework);
    const queryParams = new URLSearchParams(firework).toString();
    const url = '/postDataFetch?' + queryParams;
    console.log(JSON.stringify(firework));

    try {
        let res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(firework),
        });
    } catch (error) {
        console.error('Error sending data:', error);
    }
}
