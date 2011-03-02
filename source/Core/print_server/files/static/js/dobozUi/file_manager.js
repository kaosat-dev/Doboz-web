function FileHandler()
{
  this.mainUrl="http://192.168.0.11:8000/";
  this.availableFiles=[];
  this.uploadTimer=null; 
}
FileHandler.prototype.fetchData=function(dataUrl,successCallback,errorCallback)
    {

            response=$.ajax({
                    url: dataUrl,
                    method: 'GET',
                    dataType: 'jsonp',
                    success: successCallback,
                    error:errorCallback,
                    cache:false
                });
    }
    FileHandler.prototype.genericSuccessHandler=function (response)
    {
        console.log("Ajax sucess "+response)     
    }
    FileHandler.prototype.genericErrorHandler=function (response)
    {
        console.log("Ajax error "+response)
    }  

////////////////////////////////////////////////////////////////
//For Printable , Gcode file retrieval
FileHandler.prototype.getAvailableFiles=function ()
{
  var self = this; 
  this.fetchData(this.mainUrl+"gcodeFiles",function (response){self.availableFilesRecieved(response)});   
}
//
FileHandler.prototype.availableFilesRecieved=function(response)
{
  this.availableFiles=response.files
  $(document).trigger('Files.Recieved',[this.availableFiles]);
}
////////////////////////////////////////////////////////////////
//For Scanned pointcloud file retrieval
FileHandler.prototype.getAvailableScans=function ()
{
  var self = this; 
  this.fetchData(this.mainUrl+"scanFiles",function (response){self.scanFilesRecieved(response)});   
}

FileHandler.prototype.scanFilesRecieved=function(response)
{
  this.scanFiles=response.files
  $(document).trigger('Files.ScansRecieved',[this.scanFiles]);
}
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
//FILE UPLOAD METHODS

//Basic file extension validation
FileHandler.prototype.validateExtension=function(filePath)
{
  var ext = filePath.substring(filePath.lastIndexOf('.') + 1).toLowerCase();
  if(ext!="gcode")
  {
    return false;
  }
  return true;
}

//TODO: Move this to UI
FileHandler.prototype.resetUploadProgress=function ()
{
  $("#uploadProgressBar" ).progressbar( "option", "value", 0 );
}
////////////////////////////////////////////////////////////////
//File upload
FileHandler.prototype.UploadFile=function()
{
   if(this.validateExtension($("input[name=datafile]").val()))
   {
   $("#uploadProgress").show();
   var self = this; 
   this.uploadTimer=setInterval(function()
   { 
      self.getUploadProgress(); 
   }, 500); 
   }
   else
   {
     alert("not a good file format");
   }
}
////////////////////////////////////////////////////////////////
//For retrieval of file upload progress
FileHandler.prototype.getUploadProgress=function()
{
  var self = this; 
  this.fetchData(this.mainUrl+"uploadProgress",function (response){self.UploadProgressRecieved(response)});
  
  
}
FileHandler.prototype.UploadProgressRecieved=function(response)
{
  console.log(this)
  progress=response.progress;
  $("#uploadProgressBar" ).progressbar( "option", "value", progress );
  if( progress==100)
  {
    clearInterval(this.uploadTimer);
    this.getAvailableFiles();
    setTimeout(function(){ $("#uploadProgress").hide()}
      ,1000);
  }
}