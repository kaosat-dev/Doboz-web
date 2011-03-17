


function WebglViewer() 
{
  this.canvas=null;
  this.gl=null;
  this.shaderProgram=null;
  this.isRendering=false;
  this.drawTimer=null;
  this.drawMode=3;
  
  this.lineStripVertexPositionBuffer=[];
  this.triangleVertexPositionBuffer=[];
  this.lastPositions=null;
  this.lineStripLength=0;
  this.autoStart=false;
  this.autoRotate=false;

  this.zoomLevel=-10.0;
  this.xOffset=0.0;
  this.yOffset=0.0;
  this.mouseDown = false;
  this.lastMouseX = null;
  this.lastMouseY = null;
  this.mouseRotationMatrix = mat4.create();
  mat4.identity(this.mouseRotationMatrix);
  this.MovementModeOn=false;
}


WebglViewer.prototype.init=function()
{
      try 
      {
        this.gl = this.canvas.getContext("experimental-webgl");
        this.gl.viewportWidth =this.canvas.offsetWidth;//this.canvas.width;
        this.gl.viewportHeight = this.canvas.offsetHeight;//this.canvas.height;

      } 
      catch(e) 
      {
        console.log("WebglError "+e);
       
      }
      if (!this.gl)
      {
        console.log("Could not initialise WebGL, sorry");
    
      } 
}

WebglViewer.prototype.saveSettings=function()
{
  $.cookie({ 'webgl_viewer_autoStart': this.autoStart});
  $.cookie({ 'webgl_viewer_autoRotate': this.autoRotate});
}
WebglViewer.prototype.loadSettings=function()
{
  try
  {
  this.autoStart=eval($.cookie('webgl_viewer_autoStart'))
  this.autoRotate=eval($.cookie('webgl_viewer_autoRotate'))
  $(document).trigger('Viewer.Configured',[ {'autoStart':this.autoStart,'autoRotate':this.autoRotate}]);
  }
  catch(e)
  {
    console.log("Webgl viewer failed to retrieve settings: error "+e);
  }
  
}


WebglViewer.prototype.getShader=function (id) 
{
   
    var shaderScript = document.getElementById(id);
   
    if (!shaderScript) 
    {
      return null;
    }
    var str = "";
    var k = shaderScript.firstChild;
    while (k) 
    {
      if (k.nodeType == 3) {
        str += k.textContent;
      }
      k = k.nextSibling;
    }
 
    var shader;
    if (shaderScript.type == "x-shader/x-fragment") 
    {
      shader = this.gl.createShader(this.gl.FRAGMENT_SHADER);
    } 
    else if (shaderScript.type == "x-shader/x-vertex") 
    {
      shader = this.gl.createShader(this.gl.VERTEX_SHADER);
    } 
    else 
    {
      return null;
    }
 
    this.gl.shaderSource(shader, str);
    this.gl.compileShader(shader);
 
    if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) 
    {
      console.log(this.gl.getShaderInfoLog(shader));
      return null;
    }
 
    return shader;
}

WebglViewer.prototype.initShaders=function () 
{
    var fragmentShader = this.getShader("shader-fs");
    var vertexShader = this.getShader("shader-vs");

    this.shaderProgram = this.gl.createProgram();
    this.gl.attachShader(this.shaderProgram, vertexShader);
    this.gl.attachShader(this.shaderProgram, fragmentShader);
    this.gl.linkProgram(this.shaderProgram);
 
    if (!this.gl.getProgramParameter(this.shaderProgram, this.gl.LINK_STATUS)) 
    {
        console.log("Could not initialise shaders");
    }
 
    this.gl.useProgram(this.shaderProgram);
 
    this.shaderProgram.vertexPositionAttribute = this.gl.getAttribLocation(this.shaderProgram, "aVertexPosition");
    this.gl.enableVertexAttribArray(this.shaderProgram.vertexPositionAttribute);
    
    //this.shaderProgram.vertexColorAttribute = this.gl.getAttribLocation(this.shaderProgram, "aVertexColor");
    //this.gl.enableVertexAttribArray(this.shaderProgram.vertexColorAttribute);
 
    this.shaderProgram.pMatrixUniform = this.gl.getUniformLocation(this.shaderProgram, "uPMatrix");
    this.shaderProgram.mvMatrixUniform = this.gl.getUniformLocation(this.shaderProgram, "uMVMatrix");
    
   ////////////////////

}


WebglViewer.prototype.initBuffers =function()
{
    if (this.lastPositions==null)
    {
      this.lastPositions=[]
    }
    
    var vertices = [
         0.0,  1.0,  0.0,
        -1.0, -1.0,  0.0,
         1.0, -1.0,  0.0
    ];
    this.triangleVertexPositionBuffer = this.gl.createBuffer();
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.triangleVertexPositionBuffer);
    this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(vertices), this.gl.STATIC_DRAW);
    this.triangleVertexPositionBuffer.itemSize = 3;
    this.triangleVertexPositionBuffer.numItems = 3;
    
      
    
       this.lineStripVertexPositionBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.lineStripVertexPositionBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(this.lastPositions), this.gl.STATIC_DRAW);
        this.lineStripVertexPositionBuffer.itemSize = 3;
        this.lineStripVertexPositionBuffer.numItems =  this.lineStripLength;
       
}

WebglViewer.prototype.start=function(canvas)
{
  if(canvas!=null)
  {
  this.canvas = canvas;
  
  }
  
  
  
  
  this.init();
  this.initShaders();
  this.initBuffers();

   // Only continue if WebGL is available and working
        if (this.gl) 
        {
         this. gl.clearColor(0.15, 0.15, 0.15, 1.0);  // Set clear color to black, fully opaque
          this.gl.clearDepth(1.0);                 // Clear everything
          this.gl.enable(this.gl.DEPTH_TEST);           // Enable depth testing
          this.gl.depthFunc(this.gl.LEQUAL);            // Near things obscure far things
          this.gl.viewport(0, 0, this.canvas.offsetWidth, this.canvas.offsetHeight);
        }
        else
        {
          console.log("can't init webgl");
        }
       
  this.gl.lineWidth(3.0);
  var self = this; 

    
  this.drawTimer=setInterval(function()
      { 
      self.tick(); 
      }, 15); 
  
  this.isRendering=true;
  lastTime=new Date().getTime();
  
  

}

WebglViewer.prototype.handleKeyDown=function(event)
{
        switch(event.keyCode)
        {
          case 18:
            this.MovementModeOn=true;
           break;
          case 37://left
             this.xOffset+=0.2;
          break;
          case 39://right
            this.xOffset-=0.2;
          break;
          case 38://up
             this.yOffset+=0.2;
          break;
          case 40://down
            this.yOffset-=0.2;
          break;
         // event.preventDefault();   .
        }
}
WebglViewer.prototype.handleKeyUp=function(event)
{
  
       switch(event.keyCode)
        {
          case 18:
            this.MovementModeOn=false;
           break;
          
        }
}



WebglViewer.prototype.handleMouseDown=function(event) 
{
   this.mouseDown = true;
   this.lastMouseX = event.clientX;
   this.lastMouseY = event.clientY;

}
 
WebglViewer.prototype.handleMouseUp=function(event) 
{
   this.mouseDown = false;
}
   
WebglViewer.prototype.handleMouseMove=function(event) 
{

    if (this.mouseDown!=true) 
    {
    
        return;
     }

    
      
      
      var newX = event.clientX;
      var newY = event.clientY;

    var deltaX = newX - this.lastMouseX;
    var newRotationMatrix = mat4.create();
    mat4.identity(newRotationMatrix);
    mat4.rotate(newRotationMatrix, degToRad(deltaX / 1.1), [0, 1, 0]);

    var deltaY = newY - this.lastMouseY;
    mat4.rotate(newRotationMatrix, degToRad(deltaY / 1.1), [1, 0, 0]);

    mat4.multiply(newRotationMatrix, this.mouseRotationMatrix, this.mouseRotationMatrix);

    this.lastMouseX = newX;
    this.lastMouseY = newY;
 

}
WebglViewer.prototype.handleMouseWheel=function(event, delta, deltaX, deltaY) 
{
  
    if(delta > 0)
    {
      this.zoomLevel+=0.5;
     
    }
    else
    {
      this.zoomLevel-=0.5;
     
    }
}

   
WebglViewer.prototype.onJobStarted=function(job)
{
  if(job.type=="scan")
  {

    this.xOffset=+job.width/2.0;
    //this.yOffset=job.height/2.0;
  }
}

WebglViewer.prototype.switchDrawMode=function(mode)
{
    this.drawMode=mode;
}

WebglViewer.prototype.stop=function()
{

    
    clearInterval(this.drawTimer);
    this.isRendering=false;
}

////////////////////////////////

WebglViewer.prototype.updateBaseonReprap=function (positions,length)
{
  
    if (this.gl)
   {

      if(this.lineStripVertexPositionBuffer==null)
      {
        this.lineStripVertexPositionBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.lineStripVertexPositionBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(positions), this.gl.STATIC_DRAW);
        this.lineStripVertexPositionBuffer.itemSize = 3;
        this.lineStripVertexPositionBuffer.numItems = length;
      }
      else
      {
        this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(positions), this.gl.STATIC_DRAW);
        this.lineStripVertexPositionBuffer.itemSize = 3;
        this.lineStripVertexPositionBuffer.numItems = length;
      }
    }
      this.lastPositions=positions;
    this.lineStripLength=length;
}




WebglViewer.prototype.drawScene=function ()
{

   this.gl.viewport(0, 0, this.gl.viewportWidth, this.gl.viewportHeight);
   this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
   
   mat4.perspective(45, this.gl.viewportWidth / this.gl.viewportHeight, 0.1, 100.0, pMatrix);
   
   mat4.identity(mvMatrix);
 
   
   
   mat4.translate(mvMatrix, [this.xOffset, this.yOffset, this.zoomLevel]);

   mvPushMatrix();
   if(this.autoRotate)
   {
    
     mat4.rotate(mvMatrix, degToRad(rTri), [0.0, 0.5, 0.0]);
       mat4.rotate(mvMatrix, degToRad(22), [1.0, 0, 0.0]);
     // mat4.translate(mvMatrix, [0, -2.0, 0]);
   }
   else
   {   mat4.multiply(mvMatrix, this.mouseRotationMatrix);
   }
  // mvPushMatrix(); 
   //var l2 = this.gl.getUniformLocation(this.shaderProgram, "time");
   var ptSize = this.gl.getUniformLocation(this.shaderProgram, "pointSize");
   
   try
   {
   
     this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.lineStripVertexPositionBuffer);

     this.gl.uniform1f(ptSize, 8);
     
     this.gl.vertexAttribPointer(this.shaderProgram.vertexPositionAttribute, this.lineStripVertexPositionBuffer.itemSize, this.gl.FLOAT, false, 0, 0);
      setMatrixUniforms(this.gl,this.shaderProgram);
     this.gl.drawArrays(this.drawMode, 0, this.lineStripVertexPositionBuffer.numItems);
     ///////////////////
   
    /* this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.triangleVertexPositionBuffer);
     this.gl.vertexAttribPointer(this.shaderProgram.vertexPositionAttribute, this.triangleVertexPositionBuffer.itemSize, this.gl.FLOAT, false, 0, 0);
     setMatrixUniforms(this.gl,this.shaderProgram);
     this.gl.drawArrays(this.drawMode, 0, this.triangleVertexPositionBuffer.numItems);*/

   }
   catch(e)
   {
     console.log("bleh "+this.lineStripVertexPositionBuffer+ "error "+ e);  
   }
   mvPopMatrix(); 
}

var lastTime = 0;
var rTri=0;
var elapsed=0;
WebglViewer.prototype.animate=function() 
{
    var timeNow = new Date().getTime();
    if (lastTime != 0) {
      
       elapsed = timeNow - lastTime;

      rTri += (12 * elapsed) / 1000.0;

    }
    lastTime = timeNow;
 }
 



WebglViewer.prototype.tick=function() 
{
    
    if(this.isRendering)
    {
    this.drawScene();
    this.animate();
    }

}

WebglViewer.prototype.onJobProgressUpdated=function(progressReport)
{
  
  this.updateBaseonReprap(progressReport.positions,progressReport.positionSize);
}

 var mvMatrix = mat4.create();
    var mvMatrixStack = [];
    var pMatrix = mat4.create();
 
    function setMatrixUniforms(gl,shaderProgram) {
        gl.uniformMatrix4fv(shaderProgram.pMatrixUniform, false, pMatrix);
        gl.uniformMatrix4fv(shaderProgram.mvMatrixUniform, false, mvMatrix);
         var normalMatrix = mat3.create();
        mat4.toInverseMat3(mvMatrix, normalMatrix);
        mat3.transpose(normalMatrix);
        gl.uniformMatrix3fv(shaderProgram.nMatrixUniform, false, normalMatrix);
    }
function mvPushMatrix() {
        var copy = mat4.create();
        mat4.set(mvMatrix, copy);
        mvMatrixStack.push(copy);
    }
 
    function mvPopMatrix() {
        if (mvMatrixStack.length == 0) {
            throw "Invalid popMatrix!";
        }
        mvMatrix = mvMatrixStack.pop();
    }

 
    function degToRad(degrees) {
        return degrees * Math.PI / 180;
    }

