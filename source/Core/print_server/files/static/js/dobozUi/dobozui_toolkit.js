function DobozUi()
{
    this.defaultScanWidth=1;
    this.defaultScanHeight=1;
    this.defaultScanRes=1;
    this.firstStart=true;
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
       //////////////////////////////////////////////////////
     $( "#scanOptions button:first")
     .button
        ({
            text: true
          })
          .click(function() 
          {
          $(document).trigger('Job.Added',[{"type":"scan","width":$("#scanWidth").val(),"height":$("#scanHeight").val(),"resolution":$("#scanResolution").val()}]);
          
        });     
          
          //////////////////////////////////////////////////////
     $( "#manualControlDialog button:first").button
        ({
            text: true
          });    
          
   
         
    $("#fileUploadDialog").dialog({ autoOpen: false,width: 440 ,modal: false });
    $("#manualControlDialog").dialog({ autoOpen: false,width: 400 });
    
    
    $("#fileUploadDialog").hide();
    $("#manualControlDialog").hide();
    $("#deleteJobDialog").hide();
    
    $( "#jobList" ).sortable();

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
      
        
}
DobozUi.prototype.saveSettings=function()
{
  $.cookie({ 'reprapMgr_defaultScanWidth': this.defaultScanWidth});
  $.cookie({ 'reprapMgr_defaultScanHeight': this.defaultScanHeight});
  $.cookie({ 'reprapMgr_defaultScanRes': this.defaultScanRes});
}
DobozUi.prototype.loadSettings=function()
{
  this.defaultScanWidth=eval($.cookie('reprapMgr_defaultScanWidth'))
  this.defaultScanHeight=eval($.cookie('reprapMgr_defaultScanWidth'))
  this.defaultScanRes=eval($.cookie('reprapMgr_defaultScanRes'))
  $(document).trigger('DobozUi.Configured',[ {'defaultScanWidth':this.defaultScanWidth,'defaultScanHeight':this.defaultScanHeight,'defaultScanRes':this.defaultScanRes}]);
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
  var date="";
   for(var i=0;i<files.length;i++)
  {
   $("#fileTable" ).append("<tr id='file_"+i+"' scope='row' class=' ui-widget-content' onmousedown= $(document).trigger('Job.Added',[{'type':'print','file':'"+files[i]+"'}]);><td >"+ files[i]+ " </td><td >"+date+" </td><td style='width:50px'><span class='ui-icon ui-icon-close' style='width:20px' onclick=$(document).trigger('File.Removed',"+i+");></span></td></tr>");
  }

  
}

DobozUi.prototype.onScanListRecieved=function(scans)
{
   $("#scanTable").find("tr:gt(0)").remove();
   var date="";
   for(var i=0;i<scans.length;i++)
  {
   $("#scanTable" ).append("<tr id='scan"+i+"' scope='row' class=' ui-widget-content '><td style='width:20px'><a href='./uploads/"+scans[i]+"' target=_BLANK><span class='ui-icon ui-icon-arrowthickstop-1-s'/></a></td><td>"+ scans[i]+ "</td><td >"+date+" </td><td style='width:50px'><span class='ui-icon ui-icon-close' style='width:20px' onclick=$(document).trigger('Scan.Removed',"+i+");></span></td></tr>");
  }
    
}

////////////////////////////////////////////////////////////////
//All JOB RELATED METHODS
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
  
   $("#jobTable" ).append("<tr id='job_"+job.id+"' class='infoTable ui-widget-content' ><td style='width:50px'>"+ job.type+ " </td><td >"+options+" </td><td><span class='ui-icon ui-icon-close' style='width:20px' onclick=$(document).trigger('Job.Removed',"+job.id+");></span></td></tr>");

}

DobozUi.prototype.onJobsDelayChanged=function()
{
   var delay=$("#jobDelayField").val();
  //fire event
  $(document).trigger('Job.DelayChanged',[delay]);
}

DobozUi.prototype.onJobRemoved=function(jobId)
{$("#job_"+jobId).remove();
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
   $("#statusInfo").html("Extr T&deg;"+status.ExtruderTemp+" Bed T&deg;"+status.BedTemp);
}


DobozUi.prototype.onFileUploadClicked=function()
{
  if(!isPrinting)
  {
      selectedFile=file;
      $('#selectedFileDisplay').text(file);
  }
}
    
      