function FileManager(mainUrl)
{
  this.mainUrl=mainUrl;
  this.availableFiles=[];
  this.uploadTimer=null; 
}
FileManager.prototype.fetchData=function(dataUrl,successCallback,errorCallback)
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
    FileManager.prototype.genericSuccessHandler=function (response)
    {
        console.log("Ajax sucess "+response)     
    }
    FileManager.prototype.genericErrorHandler=function (response)
    {
        console.log("Ajax error "+response)
    }  

////////////////////////////////////////////////////////////////
//Initial retrieval of data
FileManager.prototype.init=function ()
{
  this.getAvailablePrints();
  this.getAvailableScans();
}
//For Printable , Gcode file retrieval
FileManager.prototype.getAvailablePrints=function ()
{
  var self = this; 
  this.fetchData(this.mainUrl+"filecommands/get_printFiles",function (response){self.availablePrintsRecieved(response)}); 
  
}
//
FileManager.prototype.availablePrintsRecieved=function(response)
{
  this.availableFiles=response.files
 
  $(document).trigger('Files.Recieved',[this.availableFiles]);
}
////////////////////////////////////////////////////////////////
//For Scanned pointcloud file retrieval
FileManager.prototype.getAvailableScans=function ()
{
  var self = this; 
  this.fetchData(this.mainUrl+"filecommands/get_scanFiles",function (response){self.scanFilesRecieved(response)});   
}

FileManager.prototype.scanFilesRecieved=function(response)
{
  this.scanFiles=response.files
 
  $(document).trigger('Files.ScansRecieved',[this.scanFiles]);
}
////////////////////////////////////////////////////////////////
FileManager.prototype.DeleteFile=function (file)
{ 
  var self = this; 
  this.fetchData(this.mainUrl+"filecommands/delete_"+file.type+"File?fileName="+file.name,function (response){self.fileDeleted(response)}); 
}
FileManager.prototype.fileDeleted=function(response)
{
  $(document).trigger('File.DeletionConfirmed');
}
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
//FILE UPLOAD METHODS

//Basic file extension validation
FileManager.prototype.validateExtension=function(filePath)
{
  var ext = filePath.substring(filePath.lastIndexOf('.') + 1).toLowerCase();
  if(ext!="gcode")
  {
    return false;
  }
  return true;
}

//TODO: Move this to UI
FileManager.prototype.resetUploadProgress=function ()
{
  $("#uploadProgressBar" ).progressbar( "option", "value", 0 );
}
////////////////////////////////////////////////////////////////
//File upload
FileManager.prototype.UploadFile=function()
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
FileManager.prototype.getUploadProgress=function()
{
  var self = this; 
  this.fetchData(this.mainUrl+"uploadProgress",function (response){self.UploadProgressRecieved(response)});
  
  
}
FileManager.prototype.UploadProgressRecieved=function(response)
{
  progress=response.progress;
  $("#uploadProgressBar" ).progressbar( "option", "value", progress );
  if( progress==100)
  {
    clearInterval(this.uploadTimer);
    this.getAvailablePrints();
    $("#uploadProgress").hide();
    $("#fileUploadDialog").dialog('close');
    $("#fileUploadDialog").html($("#fileUploadDialog").html());
  }
}