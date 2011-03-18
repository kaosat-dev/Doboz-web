function DobozUi()
{
    this.defaultScanWidth=1;
    this.defaultScanHeight=1;
    this.defaultScanRes=1;
    this.firstStart=true;
    this.selectedFile=null;
    
    this.camFliFlopid=0;

}

DobozUi.prototype.onDocumentReady=function()
{
    
    $("#jobProgressBar").progressbar({ value: 0 });
    $("#uploadProgressBar").progressbar({ value: 0 });
    //////////////////////////////////////////////////////
    $( "#radio" ).buttonset();
    //////////////////////////////////////////////////////
    $( "#tabs" ).tabs();
    $( "#tabs" ).bind( "tabsselect", function(event, ui) {});
    
    $( "#viewTabs" ).tabs();
    $( "#viewTabs" ).bind( "tabsselect", function(event, ui) {});
    
    //////////////////////////////////////////////////////
    $( ".jobControls button:first" ).button
        ( {
          text: true,
          icons: {
            primary: "ui-icon-triangle-1-n"
          }
        })
        .click(function() {
         // alert( "Could display a menu to select an action" );
        })
        .next().button
        ({
            icons: {primary: "ui-icon-play",},
            text: true
          })
        
 
          
          .next().button
         ({
            icons: {primary: "ui-icon-stop" }
          }
         ).next().button
         ({
            icons: {primary: "ui-icon-person" }
          }
         );
   //////////////////////////////////////////////////////
   
    $( "#machineSettingsButton").button
        ({
            icons: {primary: "ui-icon-wrench",},
            text: true
          })
         ;
     //////////////////////////////////////////////////////
   
    $( "#fileUploadButton").button
        ({
            icons: {primary: "ui-icon-arrowthickstop-1-n",},
            text: true
          })
         ;
    //////////////////////////////////////////////////////
    $( "#webglControls button:first" ).button
        ({
            icons: {primary: "ui-icon-play",},
            text: true
          }).next().button
         ({
            icons: {primary: "ui-icon-stop" },
            text: true
          }
         );
      //////////////////////////////////////////////////////
     $( "#fileUploadDialog button:first").button
        ({
            text: true
          });  
      
       $( "#deleteFileDialog button:first").button
        ({
            text: true
          }); 
       //////////////////////////////////////////////////////
     $( "#scanOptions button:first")
     .button
        ({
            text: true
          })
          .click(function() 
          {
          $(document).trigger('Job.Added',[{"type":"scan","width":$("#scanWidth").val(),"height":$("#scanHeight").val(),"resolution":$("#scanResolution").val(),"passes":$("#scanPasses").val(),"fileName":$("#scanName").val(),"saveScan":$( "#saveScanRadio").is(':checked')}]);
          
        });     
          
          //////////////////////////////////////////////////////
     $( "#manualControlDialog button:first").button
        ({
            text: true
          });    
          
   
         
    $("#fileUploadDialog").dialog({ autoOpen: false,width: 440 ,modal: false });
    $("#manualControlDialog").dialog({ autoOpen: false,width: 400 });
    $("#deleteFileDialog").dialog({ autoOpen: false,width: 400 });
    $("#stopJobDialog").dialog({ autoOpen: false,width: 400 });
    
    
    $("#fileUploadDialog").hide();
    $("#manualControlDialog").hide();
    $("#deleteJobDialog").hide();
    $("#stopJobDialog").hide();
    $("#deleteFileDialog").hide();
    
    //$( "#jobList" ).sortable();

    $( ".tab-acordeon" ).accordion({
      clearStyle: true ,autoHeight: false,collapsible: true
    });
    
    $( "#viewerAutoStartRadio").change( 
      function() {

           
           $(document).trigger('Viewer.autoStartSet',[$( "#viewerAutoStartRadio").is(':checked')]);
         
       });
      $( "#viewerAutoRotateRadio").change( 
      function() {

           
           $(document).trigger('Viewer.autoRotateSet',[$( "#viewerAutoRotateRadio").is(':checked')]);
         
       });
      $( "#drawModeRadio").change(    function() {

           
           $(document).trigger('Viewer.drawmodeSet',[$("input[name='gl_draw_options']:checked").val()]);
         
       });
      
      
      
      
     
      
      
      
      
      if(this.firstStart)
      {
       $("#container")
              .notify({ custom:false })
              .notify("create", {
                 title:"Start Notification", 
                 text:"Welcome to the 'Doboz' experimental web gui for repraps/repraps<br>Please visit <a href='http://www.kaosat.net' target='blank'>www.kaosat.net</a> and <a href='http://github.com/kaosat-dev/Doboz' target='blank'> http://github.com/kaosat-dev/Doboz</a> for more info" },
                 { custom:true ,expires: false,speed: 500});
                 
               
           this.firstStart=false;
           $.cookie({ 'dobozUi_firstStart': false});  
       }
         viewer.loadSettings();
         dobozUi.loadSettings();  
   ////////////
     
   self=this;
   this.timer=setInterval(function()
                { 
                  self.OnImageUpdateTimeout(); 
                }, 2000); 
      
}


DobozUi.prototype.fetchData=function(dataUrl,successCallback,errorCallback)
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
    DobozUi.prototype.genericSuccessHandler=function (response)
    {
      console.log("Ajax sucess "+response) 
    }
    DobozUi.prototype.genericErrorHandler=function (response)
    {
      console.log("Ajax error "+response)
    }   

DobozUi.prototype.init=function()
{
  this.loadSettings();
  this.onDocumentReady();
  

   
}
DobozUi.prototype.saveSettings=function()
{
  $.cookie({ 'reprapMgr_defaultScanWidth': this.defaultScanWidth});
  $.cookie({ 'reprapMgr_defaultScanHeight': this.defaultScanHeight});
  $.cookie({ 'reprapMgr_defaultScanRes': this.defaultScanRes});
  
}
DobozUi.prototype.loadSettings=function()
{
  try
  {
  this.firstStart=eval($.cookie('dobozUi_firstStart'))
  }
   catch(e) 
   {
      console.log("General init error  "+e);
   }
  //this.defaultScanWidth=eval($.cookie('reprapMgr_defaultScanWidth'))
  //this.defaultScanHeight=eval($.cookie('reprapMgr_defaultScanWidth'))
  //this.defaultScanRes=eval($.cookie('reprapMgr_defaultScanRes'))
  //$(document).trigger('DobozUi.Configured',[ {'defaultScanWidth':this.defaultScanWidth,'defaultScanHeight':this.defaultScanHeight,'defaultScanRes':this.defaultScanRes}]);
}

DobozUi.prototype.onViewerConfigured=function(config)
{
  $( "#viewerAutoStartRadio").attr('checked', config.autoStart);
   $( "#viewerAutoRotateRadio").attr('checked', config.autoRotate);
}




DobozUi.prototype.onScanWidthChanged=function()
{
  var scanW=$("#scanWidth").val();
  //fire event
  $(document).trigger('Scan.WidthChanged',[scanW]);
  
}
DobozUi.prototype.onScanHeightChanged=function()
{
  var scanH=$("#scanHeight").val();
  //fire event
  $(document).trigger('Scan.HeightChanged',[scanH]);
}
DobozUi.prototype.onScanResolutionChanged=function()
{
   var scanR=$("#scanResolution").val();
  //fire event
  $(document).trigger('Scan.ResolutionChanged',[scanR]);
}



////////////////////////////////////////////////////////////////
//All PRINT/SCAN file RELATED METHODS
//TODO : perhaps roll these two methods into one
DobozUi.prototype.onFileListRecieved=function(files)
{
  $("#fileTable").find("tr:gt(0)").remove();

   for(var i=0;i<files.length;i++)
  {

   $("#fileTable" ).append("<tr id='file_"+i+"' scope='row' class=' ui-widget-content' ><td onmousedown= $(document).trigger('Job.Added',[{'type':'print','file':'"+files[i].fileName+"'}]);>"+ files[i].fileName+ " </td><td >"+files[i].modDate+" </td><td style='width:50px'><span class='ui-icon ui-icon-close' style='width:20px' onclick=$(document).trigger('File.DeletionDialogRequested',"+"[{'id':'file_"+i+"','name':'"+files[i].fileName+"','type':'print'}]);></span></td></tr>");
  }
}

DobozUi.prototype.onScanListRecieved=function(scans)
{
   $("#scanTable").find("tr:gt(0)").remove();
  
   for(var i=0;i<scans.length;i++)
  {

   $("#scanTable" ).append("<tr id='scan_"+i+"' scope='row' class=' ui-widget-content '><td style='width:20px'><a href='./uploads/"+scans[i].fileName+"' target=_BLANK><span class='ui-icon ui-icon-arrowthickstop-1-s'/></a></td><td>"+ scans[i].fileName+ "</td><td >"+scans[i].modDate+" </td><td style='width:50px'><span class='ui-icon ui-icon-close' style='width:20px' onclick=$(document).trigger('File.DeletionDialogRequested',"+"[{'id':'scan_"+i+"','name':'"+scans[i].fileName+"','type':'scan'}]);></span></td></tr>");
  }
    
}

////////////////////////////////////////////////////////////////
//All JOB RELATED METHODS
DobozUi.prototype.onJobRetrievedAll=function(jobs)
{
   for(var i=0;i<jobs.length;i++)
  {
    job=jobs[i];
    var options="";
  if(job.type=="print")
  {
   options="File: "+job.file;
  }
  else if(job.type=="scan")
  {
    options="Width:"+job.width+" Height: "+job.height+" Resolution "+job.resolution;
  }
      $("#jobTable" ).append("<tr id='job_"+job.id+"' class='infoTable ui-widget-content' ><td style='width:50px'><span class='ui-icon ui-icon-star' style='width:15px;display:inline-block;' /></td> <td style='width:50px'>"+ job.type+ " </td><td >"+options+" </td><td></td><td><span class='ui-icon ui-icon-close' style='width:20px' onclick=$(document).trigger('Job.Removed',"+job.id+");></span></td></tr>");
  }
}

DobozUi.prototype.onJobAdded=function(job)
{

  var options="";
  if(job.type=="print")
  {
   options="File: "+job.file;
  }
  else if(job.type=="scan")
  {
    options="Width:"+job.width+" Height: "+job.height+" Resolution "+job.resolution;
  }
  
   $("#jobTable" ).append("<tr id='job_"+job.id+"' class='infoTable ui-widget-content' ><td style='width:50px'><span class='ui-icon ui-icon-star' style='width:15px;display:inline-block;' /><span class='ui-icon ui-icon-play' style='width:15px;display:inline-block;' ></span><span class='ui-icon ui-icon-locked' style='width:15px;display:inline-block;' ></span></td><td style='width:50px'>"+ job.type+ " </td><td >"+options+" </td><td></td><td><span class='ui-icon ui-icon-close' style='width:20px' onclick=$(document).trigger('Job.Removed',"+job.id+");></span></td></tr>");

}

DobozUi.prototype.onJobsDelayChanged=function()
{
   var delay=$("#jobDelayField").val();
  //fire event
  $(document).trigger('Job.DelayChanged',[delay]);
}

DobozUi.prototype.onJobRemoved=function(jobId)
{
  $("#job_"+jobId).remove();
}

DobozUi.prototype.onJobStarted=function(job)
{
  $( ".mainControls button:first" ).button({ label: "Job: "+job.type });
}

DobozUi.prototype.onJobProgressUpdated=function(progressReport)
{
   $("#jobProgressBar" ).progressbar( "option", "value", progressReport.progress );
  
}

DobozUi.prototype.onJobFinished=function(job)
{
  $("#job_"+job.id).remove();
   $( ".mainControls button:first" ).button({ label: "Job: none"});
  $("#jobProgressBar" ).progressbar( "option", "value", 100 );
   $("#container").notify("create", {title: 'Job: '+job.type+' Done', text: 'Job finished, machine ready.'},{ custom:true,speed: 500});     
}


DobozUi.prototype.onStatusUpdated=function(status)
{
   $("#statusInfo").html("Extr T&deg;<FONT COLOR='red'> "+status.ExtruderTemp+"</FONT> Bed T&deg; <FONT COLOR='red'>"+status.BedTemp+"</FONT>");
}


DobozUi.prototype.onFileUploadClicked=function()
{
  if(!isPrinting)
  {
      selectedFile=file;
      $('#selectedFileDisplay').text(file);
  }
}

DobozUi.prototype.onFileDeletionDialogRequested=function(file)
{ 
    this.selectedFile=file;
 
    $("#fileToDeleteField").text(file.name+" ?");
    $("#deleteFileDialog").dialog('open');
}



DobozUi.prototype.onFileDeletionConfirmed=function()
{
    $("#"+this.selectedFile.id).remove();
}

DobozUi.prototype.OnImageUpdateTimeout=function()
{
   //flip flop trick to force image update, without having to use the datetime trick
   var img_src ="/img/test.png";
   //var timestamp = new Date().getTime();   //+'?'+timestamp
   $("#camPic").attr('src',img_src+'?'+self.camFliFlopid);
   self.camFliFlopid++;
   if(self.camFliFlopid>1)
   {
     self.camFliFlopid=0;
   }

}



  


    
      