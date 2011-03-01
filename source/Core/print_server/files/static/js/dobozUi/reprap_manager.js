////////////////////////////////////////////////////////////////
//Class for managing a reprap machine
function ReprapMgr() 
{
    this.mainUrl="http://192.168.0.10:8000/";
    this.currentMode = 'scan';
    this.isJobPaused=false;
    this.isJobStarted=false;
    this.timer=null;
     ////////////////
    //TODO Reprap machine settable options
    this.units="mm";
    this.sentGodeLineEnd="/t/n";
    this.recievedGcodeEnd="ok";
    
    this.statusAutoFetch=false;
    this.statusTimer=0; //timer for machine status retrieval
    this.statusFetchInterval=-1;//in seconds

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
    
   
}
ReprapMgr.prototype.init=function()
{
     this.setupMachineStatus();
     this.getJobStatus();
}
ReprapMgr.prototype.saveSettings=function()
{
 
}
ReprapMgr.prototype.loadSettings=function()
{
  
}

 ////////////////
    ReprapMgr.prototype.fetchData=function(dataUrl,successCallback,errorCallback)
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
    ReprapMgr.prototype.genericSuccessHandler=function (response)
    {
      console.log("Ajax sucess "+response) 
    }
    ReprapMgr.prototype.genericErrorHandler=function (response)
    {
      console.log("Ajax error "+response)
    }   
    
    
    
    
    ReprapMgr.prototype.sendManualCommand=function(command)
    {
      
          var self = this; 
          this.fetchData(this.mainUrl+"printcommands/manual"+"?gcode="+command,function (response){self.genericSuccessHandler(response)});  
     }
    
    ReprapMgr.prototype.onJobAdded=function(job)
    {
      this.jobs.push(job);
      
    }
    
    ReprapMgr.prototype.onJobRemoved=function(jobId)
    {
      for (var i = 0; i <  this.jobs.length; i++)
      {
        if(this.jobs[i].id==jobId)
        {
          this.jobs.splice(i,1);
        }
      }
    }
    
    //start the current job if it has not already been started, pause it otherwise
    ReprapMgr.prototype.startPauseJob=function()  
    {
      
      
      var params="";
      if(this.isJobStarted)
      {
        if(this.isJobPaused)
        {
          
          this.isJobPaused=false;
          self=this;
          this.fetchData(this.mainUrl+this.currentMode+"commands/startpause",function (response){self.genericSuccessHandler(response)});  
           this.timer=setInterval(function()
            { 
              self.getJobProgressData(); 
            }, 100); 
        }
        else
        {
          var self = this; 
          this.fetchData(this.mainUrl+this.currentMode+"commands/startpause",function (response){self.genericSuccessHandler(response)});  
          this.isJobPaused=true;
          clearInterval(this.timer);
        }
       
      }
      else
      {
         
          if(this.jobs.length>0)
          {
            this.isJobStarted=true;
            this.readyForNextJob=false;
            this.currentJob=this.jobs.shift();
            
            this.currentJob.locked=true;
            this.currentMode=this.currentJob.type;
            this.lastPositions=[];
            this.lastPositionIndex=0;
            if(this.currentMode=="print")
            {
                params="?fileName="+this.currentJob.file;
            }
            else
            {   
                
                
                params="?width="+this.currentJob.width+"&height="+this.currentJob.height+"&resolution="+this.currentJob.resolution;
            }
                //fire event to signal job is getting started
                $(document).trigger('Job.Started',[this.currentJob]);
                var self = this; 
                this.fetchData(this.mainUrl+this.currentMode+"commands/start"+params,function (response){self.genericSuccessHandler(response)});  
                
                this.timer=setInterval(function()
                { 
                  self.getJobProgressData(); 
                }, 100); 
                
            
          }
      }
      
  
      
    }  
    
    //Stop the current Job, if any
    ReprapMgr.prototype.stopJob=function () 
    { 
        var self = this; 
        this.fetchData(this.mainUrl+this.currentMode+"commands/stop",function (response){self.genericSuccessHandler(response)});   
        clearInterval(this.timer);
          this.isJobStarted=false;
          this.isJobPaused=false;
          $(document).trigger('Job.finished',[this.currentJob])
    }
    ReprapMgr.prototype.timedTransitionToNextJob=function () 
    {
  
        var self = this; 
        this.timer=setTimeout(function()
        { 
          this.readyForNextJob=true;
          self.startPauseJob(); 
          
          }, this.jobDelay*1000); 
    }
    
    //get the status of the current print job
    ReprapMgr.prototype.getJobStatus=function()
    {
          //checks if a print/scan is already in progress
           var self = this; 
           this.fetchData(this.mainUrl+this.currentMode+"commands/status",function (response){self.onJobStatusRecieved(response)});     
    }
    
    ReprapMgr.prototype.onJobStatusRecieved=function(response)
    {
        progress=response.progress;
        lastCommand=response.lastCommand;
        jobType=response.jobType;
        if(progress>0 && progress<100)
        {
          this.isJobStarted=true;
          if(jobType=="print")
          {
              file=response.file;
              this.selectedFile=file;
          }
         
         var self=this;
          this.timer=setInterval(function()
          { 
          self.getJobProgressData(); 
          }, 100); 
          
          
        }
        else
        {
          clearInterval(this.timer);
          this.isJobStarted=false;
          this.isJobPaused=false;
        }
    }
    
    

    //get the progress and data of the current print/scan job
    ReprapMgr.prototype.getJobProgressData = function()
    {
          //checks if a print/scan is already in progress
          var self = this; 
          self.fetchData(this.mainUrl+this.currentMode+"commands/progress?LastIndex="+this.lastPositionIndex+"&blockSize="+this.streamBlockSize,function (response){self.onJobProgressDataRecieved(response)});     
    }
    
    ReprapMgr.prototype.onJobProgressDataRecieved=function(response)
    {
        //in case we get an answer even if the job was stopped
        if(!this.isJobStarted || this.isJobPaused)
        {
          return;
        }
        //alert("response "+response.jobType+" "+response.progress);
        progress=response.progress;
        
        lastCommand=response.lastCommand;
        jobType=response.jobType;
      
        if(progress>=0 && progress<100)
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
            $(document).trigger('Job.progressUpdated',[{"progress":progress,"lastCommand":lastCommand,"positions":tmpPositions,"positionSize":tmpPositions.length/3}]);

           
          } 
          catch(e)
          {
            alert("error "+e)
          }
        }
        else
        {
          clearInterval(this.timer);
          this.isJobStarted=false;
          this.isJobPaused=false;
          $(document).trigger('Job.finished',[this.currentJob])
          this.timedTransitionToNextJob();
        }
       
    }
    
    //setup the automatic status fetching of the reprap/repstrap machine
    ReprapMgr.prototype.setupMachineStatus=function()
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
    ReprapMgr.prototype.getMachineStatus=function()
    {
          //checks if a print/scan is already in progress
 
          alert("here");
           var self = this; 
           self.fetchData(this.mainUrl+"commands/status",function (response){self.onMachineStatusRecieved(response)});     
    }
    
    ReprapMgr.prototype.onMachineStatusRecieved=function(response)
    {
        
        lastCommand=response.lastCommand;
       
        //Trigger machine status update

        $(document).trigger('Status.updated',[{"ExtruderTemp":response.headTemp,"BedTemp":response.bedTemp}])
    }
    
    
