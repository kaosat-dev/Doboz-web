 /////////////////
function secondsToTime(secs)
{
    var hours = Math.floor(secs / (60 * 60));
   
    var divisor_for_minutes = secs % (60 * 60);
    var minutes = Math.floor(divisor_for_minutes / 60);
 
    var divisor_for_seconds = divisor_for_minutes % 60;
    var seconds = Math.ceil(divisor_for_seconds);
   
    var timeO = {"h": hours,"m": minutes,"s": seconds};
    return timeO;
}      
       $(document).bind("Viewer.Configured", function(e, config)
      {
        dobozUi.onViewerConfigured(config);
       });
      
       $(document).bind("Job.Added", function(e, job)
      {
        job.id=jobId;
        dobozUi.onJobAdded(job);
        reprapMgr.onJobAdded(job);
        jobId++;
       });
       
       $(document).bind("Job.Removed", function(e, jobId)
      {

          //TODO: needs to check if the job is running!! 
          dobozUi.onJobRemoved(jobId);
          reprapMgr.onJobRemoved(jobId);

       });
       
      $(document).bind("Job.Started", function(e, job)
      {
        
        dobozUi.onJobStarted(job);
        viewer.onJobStarted(job);
       });
       
      $(document).bind("Job.progressUpdated", function(e, progressReport)
      {

        subscribers = dobozUi;
        subscribers.onJobProgressUpdated(progressReport);
        viewer.onJobProgressUpdated(progressReport);
        $("#commandHistory").html(progressReport.commandHistory);
        $("#stastubar_latestCommand").html("Cmd: <FONT COLOR='red'>"+progressReport.lastCommand+"</FONT>")
        
        $("#layerDisplay").text("Layer: "+progressReport.currentLayer);
        
        timeObj=secondsToTime(progressReport.duration);
        $("#timeDisplay").text("Duration: "+(timeObj.h+" h "+timeObj.m+' m '+timeObj.s+ " s"));
         $("#stastubar_task_duration").html("Time: <FONT COLOR='red'>"+timeObj.h+"h "+timeObj.m+'m '+timeObj.s+ "s</FONT>")
        
        
      
      });
      
      $(document).bind("Job.finished", function(e, job)
      {
          //backup 3d data
          /*tmpPositions= eval(dobozUi.lastPositions);
          viewer.lastPositions=tmpPositions;
          viewer.lineStripLength=tmpPositions.length/3;
          */
          //brutish method
          if(job.type=='scan')
          {
            fileMgr.getAvailableScans();
          }
          
          dobozUi.onJobFinished(job);
        
      });
      
      $(document).bind("Job.DelayChanged", function(e, delay)
      {
         reprapMgr.jobDelay=delay
      });
      
      $(document).bind("Job.RetrievedAll", function(e, jobs)
      {
        dobozUi.onJobRetrievedAll(jobs);
         //reprapMgr.jobDelay=delay
      });
      
       $(document).bind("GeneralRefresh.Changed", function(e, frequency)
      {
         reprapMgr.onRefreshChanged(frequency);
      });
      
      $(document).bind("Status.updated", function(e, status)
      {
         dobozUi.onStatusUpdated(status);
      });
      
      $(document).bind("Machine.StatusUpdtFrequencyChanged", function(e, frequency)
      {
          
         reprapMgr.onMachineStatusFrequencyUpdated(frequency);
      });
      
      
      
       $(document).bind("Files.Recieved", function(e, files)
      {
        dobozUi.onFileListRecieved(files);
       });
       
        $(document).bind("Files.Selected", function(e, file)
      {
        alert("here")
        dobozUi.onFileSelected(file);
        reprapMgr.onFileSelected(file);
       });
       
       $(document).bind("Files.ScansRecieved", function(e, scans)
      {
        dobozUi.onScanListRecieved(scans);
       });
       
        $(document).bind("File.DeletionDialogRequested", function(e, file)
      {
        dobozUi.onFileDeletionDialogRequested(file);
       
       });
       
        $(document).bind("File.DeletionRequested", function(e, file)
      {
        //dobozUi.onFileDeletionRequested(file);
       
       });
       
        $(document).bind("File.DeletionConfirmed", function(e)
      {
          dobozUi.onFileDeletionConfirmed();
       });
       
      
       $(document).bind("Scan.ResolutionChanged", function(e, res)
      {
         reprapMgr.scanResolution=res
      });
      
       $(document).bind("Scan.WidthChanged", function(e, width)
      {
        reprapMgr.scanWidth=width
       });
       
      $(document).bind("Scan.HeightChanged", function(e, height)
      {
        reprapMgr.scanHeight=height
       });
        $(document).bind("Scan.FileNameChanged", function(e, height)
      {
        reprapMgr.scanHeight=height
       });
       
      
      $(document).bind("Viewer.autoStartSet", function(e, valid)
      {
     
        viewer.autoStart=valid;
        viewer.saveSettings();
 
       });
        $(document).bind("Viewer.autoRotateSet", function(e, valid)
      {
     
        viewer.autoRotate=valid;
        viewer.saveSettings();
        
       });
       $(document).bind("Viewer.drawmodeSet", function(e, drawMode)
      {
        
        viewer.switchDrawMode(drawMode);
        //viewer.saveSettings();
       });
       
        $(document).bind("Movement.incrementSet", function(e, moveIncrement)
      {
        
        reprapMgr.moveIncrement=moveIncrement;
        //viewer.saveSettings();
       });
      
      
      function onSelectChange()
      {
       
        var selected = $("#cssselect option:selected");
        
         document.getElementById('mainCss').href = selected.val();
      }
      

