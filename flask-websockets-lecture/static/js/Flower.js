class Flower{
    constructor(x,y,outer_col,inner_col,scalar){
        this.x = x;
        this.y = y;
        this.o_color = outer_col;
        this.i_color = inner_col;
        this.oscillation_angle =1;
        this.size = 0;
        this.scalar = scalar
    }
    drawFlower(){
        push();
       
        fill(this.i_color);
        ellipse(this.x, this.y-abs(this.size/2), this.size/1.5,this.size/1.5);

        fill(this.i_color);
        ellipse(this.x, this.y+abs(this.size/2), this.size/1.5,this.size/1.5);

        fill(this.i_color);
        ellipse(this.x+abs(this.size/2), this.y, this.size/1.5,this.size/1.5);
         
        fill(this.i_color);
        ellipse(this.x-abs(this.size/2), this.y, this.size/1.5,this.size/1.5);

         fill(this.o_color);
        ellipse(this.x,this.y, this.size/1.8);
        
        pop();
    }
    scaleFlower(){
        this.oscillation_angle+=.03;
        this.size=(sin(this.oscillation_angle)*this.scalar)
    }
}