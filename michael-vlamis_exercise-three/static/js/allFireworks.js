
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
    displayAllFireworks();

}
function displayAllFireworks() {
    for (let firework of fireworksData) {
        push();
        translate(firework.x, firework.y);
        imageMode(CENTER);
        let size = firework.size;
        image(donutImages[firework.imageIndex], 0, 0, size, size);
        pop();
    }
}