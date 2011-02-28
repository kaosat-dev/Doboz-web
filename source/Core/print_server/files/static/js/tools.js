/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
function selectionChanged(parent)
{

    
}

  function environmentSelected(parent)
        {
            //alert(parent.options[parent.selectedIndex].value);
            //
            //selected_env.text("Environment: "+parent.options[parent.selectedIndex].value)
            //selected_env.html("<strong>Environment: </strong>"+parent.options[parent.selectedIndex].value.title);
            selected_env.html("<strong>Environment: </strong>"+environments[parent.options[parent.selectedIndex].value].title);
            selected_env_status.html("<strong>Status </strong>"+environments[parent.options[parent.selectedIndex].value].status);
        }

         function sensorTypeSelected(parent)
        {
            //alert(parent.options[parent.selectedIndex].value);
            //
            //selected_env.text("Environment: "+parent.options[parent.selectedIndex].value)
            //selected_env.html("<strong>Environment: </strong>"+parent.options[parent.selectedIndex].value.title);
            //selected_env.html("<strong>Environment: </strong>"+environments[parent.options[parent.selectedIndex].value].title);
            //selected_env_status.html("<strong>Status </strong>"+environments[parent.options[parent.selectedIndex].value].status);
        }


        var alreadyFetched = {};
        var response;

        function fetchData(parent)
        {
            var dataurl = $(parent).siblings('a').attr('href');

            function onFail(XMLHttpRequest, textStatus, errorThrown)
            {
                alert(XMLHttpRequest);
                alert(textStatus);
                alert(errorThrown);
            }

            function onDataReceived(series,textstatus,XMLHttpRequest)
            {
                    var firstcoordinate = '(' + series.data[0][0] + ', ' + series.data[0][1] + ')';
                    info.text("Fetched "+series.label+ " "+firstcoordinate);

                    if (!alreadyFetched[series.label])
                    {
                            alreadyFetched[series.label] = true;
                            data.push(series);
                    }
                    else
                    {
                            data.push(series.data);
                    }
                    //TODO add handling of updated server side data
                    myFlot=$.plot(canvas, data, options);
            }

            response=$.ajax({
                    url: dataurl,
                    method: 'GET',
                    dataType: 'jsonp',
                    success: onDataReceived,
                    error:onFail,
                    cache:false
                });
        }

        function fetchAll()
        {
            fetchSensorType();
            fetchEnvironements();
        }
        function fetchSensorType()
        {
            dataurl="http://192.168.0.10:8000/get?dataType=list_sensTypes";

            function onFail(XMLHttpRequest, textStatus, errorThrown)
            {
                alert(XMLHttpRequest);
                alert(textStatus);
                alert(errorThrown);
            }
            sensorTypes=[];
            function onDataReceived(result,textstatus,XMLHttpRequest)
            {
                    sensorTypes=result.sensorTypes;
                    //alert(environments[0].status);
                    $('#sensType_dropDown').append("<option value=" + 0 + ">" + sensorTypes[0].title + "</option>");
                    $('#sensType_dropDown').append("<option value=" + 1 + ">" + sensorTypes[1].title + "</option>");
            }


            $.ajax({
                    url: dataurl,
                    method: 'GET',
                    dataType: 'jsonp',
                    success: onDataReceived,
                    error:onFail,
                    cache:false
                });
        }
        function fetchEnvironements()
        {

            dataurl="http://192.168.0.10:8000/get?dataType=list_envs";

            function onFail(XMLHttpRequest, textStatus, errorThrown)
            {
                alert(XMLHttpRequest);
                alert(textStatus);
                alert(errorThrown);
            }
            environments=[];
            function onDataReceived(result,textstatus,XMLHttpRequest)
            {
                    environments=result.environments;
                    //alert(environments[0].status);
                    $('#env_dropDown').append("<option value=" + 0 + ">" + environments[0].title + "</option>");
                    $('#env_dropDown').append("<option value=" + 1 + ">" + environments[1].title + "</option>");
            }


            $.ajax({
                    url: dataurl,
                    method: 'GET',
                    dataType: 'jsonp',
                    success: onDataReceived,
                    error:onFail,
                    cache:false
                });
        }

        function fetchLatest(parent)
        {

            dataurl="http://192.168.0.10:8000/get?dataType=toto";

            function onFail(XMLHttpRequest, textStatus, errorThrown)
            {
                alert(XMLHttpRequest);
                alert(textStatus);
                alert(errorThrown);
            }

            function onDataReceived(result,textstatus,XMLHttpRequest)
            {
                    value.text("Value:"+result.data);

                    //alert(result.data);
            }

            $.ajax({
                    url: dataurl,
                    method: 'GET',
                    dataType: 'jsonp',
                    success: onDataReceived,
                    error:onFail,
                    cache:false
                });
            setTimeout(fetchLatest, 2000);

        }

        function pollingFetch(parent)
        {

            dataurl="http://192.168.0.10:8000/get?dataType=temperature";
            //data = [];
            //alreadyFetched = {};
           // myFlot=$.plot(canvas, data, options);
            function onFail(XMLHttpRequest, textStatus, errorThrown)
            {
                alert(XMLHttpRequest);
                alert(textStatus);
                alert(errorThrown);
            }

            function onDataReceived(series,textstatus,XMLHttpRequest)
            {
                    var firstcoordinate = '(' + series.data[0][0] + ', ' + series.data[0][1] + ')';
                    //info.text("Fetched "+series.label+ " "+firstcoordinate);

                   if (!alreadyFetched[series.label])
                    {
                            alreadyFetched[series.label] = true;
                            data.push(series);


                    }
                    else
                    {
                             //alreadyFetched[series.label] = true;
                            data.push(series.data);
                   }
                    //TODO add handling of updated server side data
                    //data=[series.data];
                    //data.push(series.data);
                    myFlot=$.plot(canvas, [series], options);
            }

            response=$.ajax({
                    url: dataurl,
                    method: 'GET',
                    dataType: 'jsonp',
                    success: onDataReceived,
                    error:onFail,
                    cache:false
                });


            setTimeout(pollingFetch, 3000);

        }