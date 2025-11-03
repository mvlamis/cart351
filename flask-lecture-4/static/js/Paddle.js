class Paddle{
    constructor(x,y,sizeW,sizeH,color){
        this.x = x;
        this.y = y;
        this.sizeW = sizeW;
        this.sizeH = sizeH;
        this.color = color;
        this.velocity = {
            x:5,
            y:0
        }
    }

    display(){
        push();
        fill(this.color);
        rectMode(CORNER);
        rect(this.x,this.y,this.sizeW,this.sizeH);
        pop();
 }
 moveRight(){
    if((this.x+this.sizeW)< width)
        this.x +=this.velocity.x
 }

  moveLeft(){
    if(this.x>0)
    this.x -=this.velocity.x
 }
 checkCollisionWithBall(ball){
    if(ball.x > this.x && ball.x<=this.x+this.sizeW){
        if(ball.y > this.y && ball.y<=this.y+this.sizeH){
            ball.velocity.y*=-1;
            if(ball.x >this.x+this.sizeW/2){
                ball.velocity.x =1;
            }
            else{
                ball.velocity.x =-1;
            }

    }

 }
}
}