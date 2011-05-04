 /////////////////
      
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
        $("#lastCommand").text("LastCommand "+lastCommand);
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
      

