


function WebglViewer() 
{
  this.canvas=null;
  this.gl=null;
  this.shaderProgram=null;
  this.isRendering=false;
  this.drawTimer=null;
  
  
  this.lineStripVertexPositionBuffer=[];
  this.lastPositions=null;
  this.lineStripLength=0;
  this.autoStart=false;

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
}
WebglViewer.prototype.loadSettings=function()
{
  this.autoStart=eval($.cookie('webgl_viewer_autoStart'))
  $(document).trigger('Viewer.Configured',[ {'autoStart':this.autoStart}]);
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
    
    this.shaderProgram.vertexColorAttribute = this.gl.getAttribLocation(this.shaderProgram, "aVertexColor");
    this.gl.enableVertexAttribArray(this.shaderProgram.vertexColorAttribute);
 
    this.shaderProgram.pMatrixUniform = this.gl.getUniformLocation(this.shaderProgram, "uPMatrix");
    this.shaderProgram.mvMatrixUniform = this.gl.getUniformLocation(this.shaderProgram, "uMVMatrix");
    
   
}
var triangleVertexPositionBuffer;
var vertices = [
         0.0,  1.0,  0.0,
        -1.0, -1.0,  0.0,
         1.0, -1.0,  0.0
    ];
WebglViewer.prototype.initBuffers =function()
{
    if (this.lastPositions==null)
    {
      this.lastPositions=[]
    }
    /*triangleVertexPositionBuffer = this.gl.createBuffer();
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, triangleVertexPositionBuffer);
    this.gl.bufferData(this.gl.ARRAY_BUFFER, new Float32Array(vertices), this.gl.STATIC_DRAW);
    triangleVertexPositionBuffer.itemSize = 3;
    triangleVertexPositionBuffer.numItems = 3;*/
    
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
       
  
  var self = this; 
    
  this.drawTimer=setInterval(function()
      { 
      self.tick(); 
      }, 15); 
  
  this.isRendering=true;
  lastTime=new Date().getTime();
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
   
   perspective(45, this.gl.viewportWidth / this.gl.viewportHeight, 0.1, 100.0);
   loadIdentity();
   
   mvPushMatrix(); 
   //mvTranslate([-2.5, 0.0, -7.0]);
     mvTranslate([-1.5, 0.0, -20.0]);
   mvRotate(rTri, [1, 1, 1]);
    var l2 = this.gl.getUniformLocation(this.shaderProgram, "time");
   try
   {
     this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.lineStripVertexPositionBuffer);
     this.gl.uniform1f(l2, elapsed);
     this.gl.vertexAttribPointer(this.shaderProgram.vertexPositionAttribute, this.lineStripVertexPositionBuffer.itemSize, this.gl.FLOAT, false, 0, 0);
     setMatrixUniforms(this.gl,this.shaderProgram);
     this.gl.drawArrays(this.gl.LINE_STRIP, 0, this.lineStripVertexPositionBuffer.numItems);
     ///////////////////
     /*this.gl.bindBuffer(this.gl.ARRAY_BUFFER, triangleVertexPositionBuffer);
     this.gl.uniform1f(l2, elapsed);
     this.gl.vertexAttribPointer(this.shaderProgram.vertexPositionAttribute, triangleVertexPositionBuffer.itemSize, this.gl.FLOAT, false, 0, 0);
     setMatrixUniforms(this.gl,this.shaderProgram);
     this.gl.drawArrays(this.gl.TRIANGLES, 0, triangleVertexPositionBuffer.numItems);*/
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

var mvMatrix;
   var mvMatrixStack = [];
   
    function mvPushMatrix(m) {
    if (m) {
      mvMatrixStack.push(m.dup());
      mvMatrix = m.dup();
    } else {
      mvMatrixStack.push(mvMatrix.dup());
    }
  }
 
  function mvPopMatrix() {
    if (mvMatrixStack.length == 0) {
      throw "Invalid popMatrix!";
    }
    mvMatrix = mvMatrixStack.pop();
    return mvMatrix;
  }
   
  function loadIdentity() {
    mvMatrix = Matrix.I(4);
  }
 
 
  function multMatrix(m) {
    mvMatrix = mvMatrix.x(m);
  }
 
 
  function mvTranslate(v) {
    var m = Matrix.Translation($V([v[0], v[1], v[2]])).ensure4x4();
    multMatrix(m);
  }
   function mvRotate(ang, v) {
    var arad = ang * Math.PI / 180.0;
    var m = Matrix.Rotation(arad, $V([v[0], v[1], v[2]])).ensure4x4();
    multMatrix(m);
  }
 
  var pMatrix;
  function perspective(fovy, aspect, znear, zfar) {
    pMatrix = makePerspective(fovy, aspect, znear, zfar);
  }
 
 
  function setMatrixUniforms(gl,shaderProgram) 
  {
    gl.uniformMatrix4fv(shaderProgram.pMatrixUniform, false, new Float32Array(pMatrix.flatten()));
    gl.uniformMatrix4fv(shaderProgram.mvMatrixUniform, false, new Float32Array(mvMatrix.flatten()));
  }
 

