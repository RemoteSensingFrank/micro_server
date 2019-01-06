var ratio=1.0;
var detectOperation={
    current_type:0,
    //select machine model
    FastRcnnModel:function(){
        $("#selectedModel").val("FASTRCNN");
    },

    //open file with the machine model
    OpenFastRCNN:function(){
        _this=this;
        $("#openFile").change(function(e){ 
            var reader = new FileReader();
            var img=new Image();
            reader.readAsDataURL(e.target.files[0]);
            reader.onloadstart=function () {
                console.log('文件读取......')
            };
            //操作完成
            reader.onload = function(e){
                //file 对象的属性
                img.setAttribute('src',reader.result);
                img.onload=function(){
                    var c=document.getElementById("imgCanvas");  
                    var ctx=c.getContext("2d");  
                    ctx.clearRect(0,0,c.width,c.height); 
                    ratio=Math.min(900.0/img.width,500.0/img.height);
                    ctx.drawImage(img, 0, 0,img.width,img.height,0,0,img.width*ratio,img.height*ratio); 
                }
            };
            


        })
    }, 



}

function FastRcnnModel(){
    detectOperation.FastRcnnModel();
    detectOperation.current_type = 1;
}

function openImage(){
    if(detectOperation.current_type==1){
        detectOperation.OpenFastRCNN();
    }
}
function getRandomColor(){ 
    return "#"+("00000"+((Math.random()*16777215+0.5)>>0).toString(16)).slice(-6); 
} 
function detect(){
    console.log($("#openFile")[0]);
    files=$("#openFile")[0].files;
    if(files.length>0){
        var form = new FormData(); 
        form.append('file',files[0]);
        $.ajax({ 
            url:"http://localhost:8082/mlserver/v1.0.0.0/fastrcnn/detect", 
            type:"post", 
            data:form, 
            processData:false, 
            contentType:false, 
            success:function(res){ 
                var str=""
                var items=JSON.parse(res)
                for(idx in items){
                    var item=items[idx];
                    var c=document.getElementById("imgCanvas");  
                    var ctx=c.getContext("2d");   
                    str+=JSON.stringify(item)+"\n";
                    ctx.strokeStyle= getRandomColor();
                    ctx.lineWidth=3;
                    x1=item["box"][0]*ratio;
                    y1=item["box"][1]*ratio;
                    x2=item["box"][2]*ratio;
                    y2=item["box"][3]*ratio;
                    ctx.strokeRect(Math.min(x1,x2),Math.min(y1,y2), Math.max(x1,x2),Math.max(y1,y2));
                }
                if(str==""){
                    str="Nothing was detected";
                }
                $("#recongnizeVis").val(str);
            }, 
            error:function(err){ 
             alert("网络连接失败,稍后重试",err); 
            } 
           }); 
    }
}