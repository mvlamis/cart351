class Brick{
    constructor(x,y,sizeW,sizeH,color){
        this.x = x;
        this.y = y;
        this.sizeW = sizeW;
        this.sizeH = sizeH;
        this.color = color;
    }

    display(){
        push();
        fill(this.color);
        rectMode(CORNER);
        rect(this.x,this.y,this.sizeW,this.sizeH);
        pop();
 }
}