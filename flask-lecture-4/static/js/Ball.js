class Ball{
    constructor(x,y,sizeW,sizeH,color,strokeColor){
        this.x = x;
        this.y = y;
        this.sizeW = sizeW;
        this.sizeH = sizeH;
        this.color = color;
        this.velocity = {
            x:0,
            y:4
        };
        this.strokeColor = strokeColor;


    }

    display(){
        push();
        fill(this.color);
        rectMode(CENTER);
        strokeWeight(2)
        stroke(this.strokeColor);
        ellipse(this.x,this.y,this.sizeW,this.sizeH);
        pop();


    }
    move(){
        this.x+=this.velocity.x;
        this.y+=this.velocity.y;

    }

    checkCollWithLeftAndRight(){
         if(this.x > width || this.x<=0){
        this.velocity.x*=-1;
        }
    }

    checkColWithBottom(){
        //top
        if(this.y <0){
        this.velocity.y*=-1;
        }
        //bottom
        if(this.y>height){
      
            this.y = height/2;
            this.velocity.y =0 ;
            this.velocity.x =0;
            gameState = "pause";
            
        }
    }

    checkCollWithBricks(bricks){
        for (let i =bricks.length-1; i>=0;i--){
           let distance = dist(
            bricks[i].x+bricks[i].sizeW/2,
            bricks[i].y+bricks[i].sizeH/2,
            this.x,
            this.y,

           )
           if (distance < bricks[i].sizeW/2){
            // remove brick
            bricks.splice(i,1);
            //updateScore
            score+=10;
            document.querySelector("#p5Score").innerHTML = `SCORE: ${score}`
            ball.velocity.y*=-1;
            return
           }
        }
    }
    update(){
    //move the ball
    this.move();
    //check collision of ball with left, right 
    this.checkCollWithLeftAndRight();
    //check coll top and bottom
    this.checkColWithBottom();
    }
    reset(){
        this.velocity.y = 3
    }
}