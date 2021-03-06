////////////////////////////////////////////////////////////////
//Class for managing a reprap machine
function ReprapManager(mainUrl) 
{
    this.mainUrl=mainUrl;
    this.isJobPaused=false;
    this.isJobStarted=false;
    this.jobStatusInterval=0.1;//in seconds
    this.timer=null;
     ////////////////
    //TODO Reprap machine settable options
    this.units="mm";
    this.sentGodeLineEnd="/t/n";
    this.recievedGcodeEnd="ok";
    
    this.statusAutoFetch=false;
    this.statusTimer=0; //timer for machine status retrieval
    this.statusFetchInterval=10;//in seconds!!!WARNING!! in the current version (march 21 2011 if you want a status update every n seconds you need to set the inteval
      //to n/2 seconds)

    //pseudo "streaming" for 3d data
    this.streamBlockSize=3;//how many points do we get in one pass
    this.lastPositions=[];
    this.lastPositionIndex=0;
    
    //Jobs   
    this.jobs=[];
    this.jobsId=Array();
    this.currentJob=null;
    this.readyForNextJob=true;
    this.jobDelay=5;//in seconds
    this.moveIncrement=1;
    
    this.xPos=0.0;
    this.yPos=0.0;
    this.zPos=0.0;
    
   
}
ReprapManager.prototype.init=function()
{
     this.setupMachineStatus();
     this.getJobStatus();
}
ReprapManager.prototype.saveSettings=function()
{
 
}
ReprapManager.prototype.loadSettings=function()
{
  
}

 ////////////////
    ReprapManager.prototype.fetchData=function(dataUrl,successCallback,errorCallback)
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
    ReprapManager.prototype.genericSuccessHandler=function (response)
    {
      console.log("Ajax sucess "+response) 
    }
    ReprapManager.prototype.genericErrorHandler=function (response)
    {
      console.log("Ajax error "+response)
    }   
    
    
    
    
    ReprapManager.prototype.sendManualCommand=function(command)
    {
      
          var self = this; 
          this.fetchData(this.mainUrl+"printcommands/manual"+"?gcode="+command,function (response){self.genericSuccessHandler(response)});  
     }
    
    ReprapManager.prototype.onJobAdded=function(job)
    {
      this.jobs.push(job);
      
    }
    
    ReprapManager.prototype.onJobRemoved=function(jobId)
    {
      for (var i = 0; i <  this.jobs.length; i++)
      {
        if(this.jobs[i].id==jobId)
        {
          this.jobs.splice(i,1);
        }
      }
    }
    
    ReprapManager.prototype.sendMoveCommand=function(command)
    {
        var self = this; 
        this.fetchData(this.mainUrl+"printcommands/manual"+"?gcode=G91", function (response){self.genericSuccessHandler(response)});  
        var completeCommand=command;
        if(command!="G28")
        {
          completeCommand+=+this.moveIncrement;
        }
        this.fetchData(this.mainUrl+"printcommands/manual"+"?gcode="+completeCommand+"F120",function (response){self.genericSuccessHandler(response)});  
        
    }
    
    //when the task confirmation answer has been recieved from the server
    ReprapManager.prototype.taskConfirmationRecieved=function(confirmation)
    {
      
    }
    //initialize a new task
     ReprapManager.prototype.initTask=function()
     {
       params="?fileName="+this.currentJob.file;
       this.fetchData(this.mainUrl+this.currentJob.type+"commands/start"+params,function (response){self.genericSuccessHandler(response)});  
       //get task confirmation from server
     }
    //start the current job if it has not already been started, pause it otherwise
    ReprapManager.prototype.startPauseJob=function()  
    {
      
      
      var params="";
      if(this.isJobStarted)//when pausing a task
      {
        
        if(this.isJobPaused)
        {
          
          this.isJobPaused=false;
          self=this;
          this.fetchData(this.mainUrl+this.currentJob.type+"commands/startpause",function (response){self.genericSuccessHandler(response)});  
           this.timer=setInterval(function()
            { 
              self.getJobProgressData(); 
            }, this.jobStatusInterval*1000); 
        }
        else
        {
          var self = this; 
          this.fetchData(this.mainUrl+this.currentJob.type+"commands/startpause",function (response){self.genericSuccessHandler(response)});  
          this.isJobPaused=true;
          clearInterval(this.timer);
        }
       
      }
      else//when starting a task
      {
         
          if(this.jobs.length>0)
          {
            this.isJobStarted=true;
            this.readyForNextJob=false;
            this.currentJob=this.jobs.shift();
            
            this.currentJob.locked=true;
            this.lastPositions=[];
            this.lastPositionIndex=0;
            if(this.currentJob.type=="print")
            {
                params="?fileName="+this.currentJob.file;
                
               
            }
            else
            {   
                
                
                params="?width="+this.currentJob.width+"&height="+this.currentJob.height+"&resolution="+this.currentJob.resolution+"&passes="+this.currentJob.passes+"&fileName="
                +this.currentJob.fileName+"&saveScan="+this.currentJob.saveScan ;
            }
                //fire event to signal job is getting started
                $(document).trigger('Job.Started',[this.currentJob]);
                var self = this; 
                this.fetchData(this.mainUrl+this.currentJob.type+"commands/start"+params,function (response){self.genericSuccessHandler(response)});  
                
                this.timer=setInterval(function()
                { 
                  self.getJobProgressData(); 
                }, self.jobStatusInterval*1000); 
                
            
          }
      }
      
  
      
    }  
    
    //Stop the current Job, if any
    ReprapManager.prototype.stopJob=function () 
    { 
        var self = this; 
        this.fetchData(this.mainUrl+this.currentJob.type+"commands/stop",function (response){self.genericSuccessHandler(response)});   
        clearInterval(this.timer);
          this.isJobStarted=false;
          this.isJobPaused=false;
          $(document).trigger('Job.finished',[this.currentJob])
    }
    ReprapManager.prototype.timedTransitionToNextJob=function () 
    {
  
        /*var self = this; 
        this.timer=setTimeout(function()
        { 
          this.readyForNextJob=true;
          self.startPauseJob(); 
          
          }, this.jobDelay*1000); */
    }
    
    //get the status of the current print job
    ReprapManager.prototype.getJobStatus=function()
    {
          //checks if a print/scan is already in progress
           var self = this; 
           this.fetchData(this.mainUrl+"commands/jobStatus",function (response){self.onJobStatusRecieved(response)});     
    }
    
    ReprapManager.prototype.onJobStatusRecieved=function(response)
    {
       
       //Add active task first
        current=jQuery.parseJSON(response.current)
        
        if(current.running)
        {
          this.currentJob=current.task;   
          this.isJobStarted=true;
        
          var self=this;
          this.timer=setInterval(function()
          { 
          self.getJobProgressData(); 
          }, self.jobStatusInterval*1000);  
        }
        else
        {
          clearInterval(this.timer);
          this.isJobStarted=false;
          this.isJobPaused=false;
        }
        
        jobs=response.tasks;
  
        for(var i=0;i<jobs.length;i++)
        {
          var job = jQuery.parseJSON(jobs[i]);
          this.jobs.push(job)
        }
        $(document).trigger('Job.RetrievedAll',[this.jobs]); 
        
    }
    
    

    //get the progress and data of the current print/scan job
    ReprapManager.prototype.getJobProgressData = function()
    {
          //checks if a print/scan is already in progress
          var self = this; 
          self.fetchData(this.mainUrl+this.currentJob.type+"commands/progress?LastIndex="+this.lastPositionIndex+"&blockSize="+this.streamBlockSize,function (response){self.onJobProgressDataRecieved(response)});     
    }
    
    ReprapManager.prototype.onJobProgressDataRecieved=function(response)
    {
        //in case we get an answer even if the job was stopped
        if(!this.isJobStarted || this.isJobPaused)
        {
          return;
        }
        //alert("response "+response.jobType+" "+response.progress);
        progress=response.progress;
        
        
        commandHistory=eval(response.commandHistory);
        lastCommand=commandHistory[0];
        commandHistory=commandHistory.join("<br>");
        currentLayer=response.layer;
        duration=response.duration;
        jobType=response.jobType;
      
        if(progress>=0 )
        {
         
          try
          {
            recievedPositions=response.positions;

            var tmpPositions= eval(recievedPositions);
            //update the index of the last recieved position (divided by 3 to account for the x,y,z components)
            this.lastPositionIndex+=tmpPositions.length/3;
            
            this.lastPositions=this.lastPositions.concat(tmpPositions);
            tmpPositions= eval(this.lastPositions);
            
            //fire event
            $(document).trigger('Job.progressUpdated',[{"progress":progress,"commandHistory":commandHistory,"lastCommand":lastCommand,"currentLayer":currentLayer,"duration":duration,"positions":tmpPositions,"positionSize":tmpPositions.length/3}]);

           
          } 
          catch(e)
          {
            alert("error "+e)
          }
        }
        if (progress>=100)
        {
          clearInterval(this.timer);
          this.isJobStarted=false;
          this.isJobPaused=false;
          $(document).trigger('Job.finished',[this.currentJob])
          this.timedTransitionToNextJob();
        }
       
    }
    
    //setup the automatic status fetching of the reprap/repstrap machine
    ReprapManager.prototype.setupMachineStatus=function()
    {
      if(this.statusAutoFetch)
      {
      var self=this;
      this.statusTimer=setInterval(function()
          { 
          self.getMachineStatus(); 
          }, this.statusFetchInterval*1000); 
       }
    }
    //get the status of the reprap/repstrap machine
    ReprapManager.prototype.getMachineStatus=function()
    {
          //checks if a print/scan is already in progress

           var self = this; 
           self.fetchData(this.mainUrl+"commands/machineStatus",function (response){self.onMachineStatusRecieved(response)});     
    }
    
    ReprapManager.prototype.onMachineStatusRecieved=function(response)
    {
        
        //lastCommand=response.lastCommand;
       
        //Trigger machine status update

        $(document).trigger('Status.updated',[{"ExtruderTemp":response.headTemp,"BedTemp":response.bedTemp}])
    }
    
    ReprapManager.prototype.onMachineStatusFrequencyUpdated=function(frequency)
    {   
      clearInterval(this.statusTimer);
        this.statusFetchInterval=frequency;
        if(frequency>0)
        {
          this.statusAutoFetch=true;
          this.setupMachineStatus();
        }
        else
        {
          this.statusAutoFetch=false; 
        }
    }
    
ReprapManager.prototype.onRefreshChanged=function(frequency)
{
  alert("here")
  this.jobStatusInterval=frequency;
}
