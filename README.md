# 微服务架构初探
&nbsp;&nbsp;&nbsp;&nbsp;本项目作为我进入微服务架构的第一个尝试性的项目，我将从数据存储，服务注册与管理，服务认证再到第三方应用这几个方面第微服务架构进行梳理和研究。实际上虽然对于微服务架构略有了解但是了解还不够深刻，对于其优缺点了解的也不多，之所以想使用微服务架构主要目的是为了在工作中提高开发的可复用性，避免过多的重复开发工作，另外使用微服务架构也便于进行扩展，另外也想通过对微服务架构的研究探索协作开发的模式和方法。

## 采用的技术与框架：
* Python 3.X 使用Python一方面是因为自己对Python相对来说比较熟悉，另一方面是因为想要在应用中集成深度学习框架；
* 基于Python的轻量级服务器框架：Flask以及Flask所包含的一系列库；
* NoSQL数据存储：采用的是MongoDB进行数据存储，至于为什么选择MongoDB主要因为它比较火没有别的原因；
* 内存数据库：实际上这一层可有可无，但是如果做服务注册于服务发现一般都需要，采用Redis，因为我比较熟悉；
* Consul，做服务注册和服务发现的框架类似于zookeeper,为什么选用consul而不是zookeeper，我也不知道，就是一时兴起；
* Nginx负载，实际上不确定是否需要做反向代理或者负载均衡，不过Nginx使用起来确实方便；
* Docker相关组件，Docker这个东西主要是方便环境的部署，否则这么多组件在一台机器上不进行隔离总是很难去管理，主要是可以通过dockfile直接构建统一的环境，相对来书比较方便；

## 1. 数据存储
&nbsp;&nbsp;&nbsp;&nbsp;从准备开启这个项目的时候就打算做一个数据存储的服务，因为数据存储是极其迫切而且广泛而且迫切的需求，几乎对于任何应用都会有这个需求，因此首先我想到了将数据存储拆分为一个微服务；数据存储微服务系统架构为：  
<center><image src="https://blogimage-1251632003.cos.ap-guangzhou.myqcloud.com/%E6%95%B0%E6%8D%AE%E5%AD%98%E5%82%A8%E7%BB%93%E6%9E%84%E5%9B%BE.JPG"/></center>

### 1.1 数据存储
&nbsp;&nbsp;&nbsp;&nbsp;最初设计是完全通过MongoDB对所有文件进行存储，由于考虑到并不是所有用户都考虑安装MongDB，另外如果有用户有需求能够在服务器上看到原始数据，在这样的情况下使用MongoDB进行数据存储是不合适的。所以最终决定同时支持文件存储与数据库存储，对于文件存储不考虑分布式，仅仅支持集中式存储。对于数据库存储则有两种情况：如果文件大小比较小，则直接以二进制方式读取文件在数据库中存储二进制文件；如果文件大小比较大，则通过GridFS对文件进行分片存储。

### 1.2 文件操作
&nbsp;&nbsp;&nbsp;&nbsp;为了使得文件存储服务更加具有通用性，对于文件存储需要定义常见的操作，在文件服务中定义的操作包括：1）文件上传；2）文件下载；3）文件删除；4）文件查看，以文件夹列表形式查看；5）文件移动；以上5个操作中前三个是基本操作，相对比较简单，后两个操作属于扩展操作相对比较麻烦。

### 1.3 文件服务器RESTful接口约定
&nbsp;&nbsp;&nbsp;&nbsp;为了对接口进行统一，对于文件服务我们采用动词+名词的形式编写接口，接口API形式为：
http://XXXX/XXX/XXX/动词短语/目标数据或文件名

## 2 关于服务注册于发现Consul

### 2.1 微服务与SOA
&nbsp;&nbsp;&nbsp;&nbsp;对于微服务的应用来说由于客户端以及服务端应用接口特别多而且复杂，对于各个客户端之间的通信是一件很复杂得事情，通常情况下一个客户端出现了问题而停止或者更换了端口或者部署机器的地址都会导致其他与之相关联的服务都需要切换端口和IP，这会带来特别大的影响，为了降低服务部署和修改带来的影响于是产生了服务注册于发现的机制。不管什么架构设计，脱离了需求来谈架构就是空谈，但是对于一个公司有着许多不同的业务板块，每个板块之间基本独立但是又有区分，因此使用微服务的架构就是很有必要的了（避免单个服务做得过大导致一旦出现问题整个系统崩溃），提到服务注册和服务发现就不得不提一下微服务的构架，如果采用单体服务的模式，整个系统前后端统一，单体化部署使用服务注册于服务发现的框架反而增加了程序负担这样就得不偿失了：  
微服务这个概念实际上相对来说比较新，从2012年提出到现在也才经过6年的时间，实际上从微服务被普遍认可和接收也就从2015年开始，我前几天读完了一本关于微服务架构的书也对微服务有了些了解，实际上整个微服务就是我们程序设计中的高内聚低耦合的集中体现。谈到微服务就不能不提SOA，这两种架构之间有着千丝万缕的联系，我实际上也没有真正执行过SOA架构或者微服务架构的应用（以后会执行的~)我只能谈谈我的理解了，对于一个应用来说，采用SOA架构主要过程是首先对业务整体情况进行了解，然后将整体业务拆分为独立的业务逻辑，然后对每一块业务逻辑流程进行分别开发，最后进行集成；而采用微服务的架构可能拆分得更加细粒度，举一个例子如图：  
<center><img src="https://blogimage-1251632003.cos.ap-guangzhou.myqcloud.com/%E5%BE%AE%E6%9C%8D%E5%8A%A1vsSOA.jpeg"></center>    

图片来自[CSDN博客](https://blog.csdn.net/u011389515/article/details/80546084)侵删联系（wuwei_cug@163.com）上面一张图很清晰的说明了SOA与微服务之间的差别，SOA以业务逻辑为粒度构建应用，而微服务架构构建更加细的粒度的独立应用，然后将应用组合起来形成业务逻辑。简单的来说就是对于服务的理解有差异，当然实际上SOA还有EBS企业总线，数据总线等概念，在这里就不详细的描述了。  
### 2.2 Consul理解
&nbsp;&nbsp;&nbsp;&nbsp;从上图中可以看到对于一件简单的应用微服务会将其拆分为很多服务然后提供接口，那么实际上这么多服务的管理自然而然就成为了一个需要考虑的问题，实际上对于这个问题SOA也出现过，而SOA采用一个很复杂的逻辑EBS总线去管理所有服务间的通信与调度以及服务的健康检查，实际上微服务并不需要这么一个复杂得逻辑，因为微服务本身的接口很清晰应用服务之间逻辑界限很明确，因此不需要一个过于复杂得调度总线，但是也需要一个服务注册于服务发现的管理，这个就是我们要着重介绍的Consul，在这里我只介绍Consul的使用以及服务的注册，更多的内容还在摸索当中：  
&nbsp;&nbsp;&nbsp;&nbsp;Consul的架构如图：  
<center><img src="https://blogimage-1251632003.cos.ap-guangzhou.myqcloud.com/consul%E7%BB%93%E6%9E%84.png"/></center>  

上面这张图示从[官网](https://www.consul.io/docs/internals/architecture.html)下载下来的图描述了整个微服务的架构，有兴趣深度了解的可以参考我的[博客](https://wuweiblog.com/2018/12/31/concul%E6%9C%8D%E5%8A%A1%E6%B3%A8%E5%86%8C%E4%B8%8E%E5%8F%91%E7%8E%B0/)或者官网教程，随之还有官网的描述，英文好的同学可以直接看原文，我在博客上也有一些自己的理解。  
### 2.3 Consul的使用
&nbsp;&nbsp;&nbsp;&nbsp;提了一大堆的介绍，从开发的角度说一下Consul的使用，因为死单机所以我采用的是单机Docker部署的方式，安装环境为Windows10 开发语言为python3.6.x。首先运行consul:[参考网上教程](https://livewyer.io/blog/2015/02/05/service-discovery-docker-containers-using-consul-and-registrator/)运行了一个单节点的consul，这个是最简单的运行，多节点就是添加节点，这个以后再说。运行完成之后在浏览器可以看到如下页面：  
<center><img src="https://blogimage-1251632003.cos.ap-guangzhou.myqcloud.com/consul-ui.jpg"/></center>  
&nbsp;&nbsp;&nbsp;&nbsp;从上面的界面上可以看到服务运行的状态信息，有一个consul 的节点，另外运行了一个datastorage的服务，不过这个服务failling，是一个失败的服务，因为我停掉了服务器。我们可以根据上面的参考教材通过命令去注册服务，当然我这里使用python-consul直接在服务启动的时候进行注册，具体的代码为:  

```python
import sys
import mongoRoute as MongoRoute
import instance
import consul

api = instance.api
app = instance.app
conf= instance.conf
#help info 
@app.route('/filestorage/v1.0.0/help') 
def help(): 
   return 'help info' 

#for health check
@app.route('/filestorage/v1.0.0/check', methods=['GET'])  
def check():
   return 'success'

api.add_resource(MongoRoute.LargeFileUploadChunkMongo,   '/filestorage/v1.0.0.0/mongodb/uploadlargechunk')
api.add_resource(MongoRoute.LargeFileUploadFinishedMongo,'/filestorage/v1.0.0.0/mongodb/uploadlargefinished')
api.add_resource(MongoRoute.SmallFileUploadMongo,        '/filestorage/v1.0.0.0/mongodb/uploadsmall')

api.add_resource(MongoRoute.LargeFileDownloadMongo,      '/filestorage/v1.0.0.0/mongo/downloadlarge')
api.add_resource(MongoRoute.SmallFileDownloadMongo,      '/filestorage/v1.0.0.0/mongo/downloadsmall')
api.add_resource(MongoRoute.SmallFileDownloadAsFileMongo,'/filestorage/v1.0.0.0/mongo/downloadsmallasfile')


#services register
def consul_service_register():
   client = consul.Consul()
   service_id = "datastorage-localhost:8081"
   httpcheck  = "http://192.168.1.25:8081/filestorage/v1.0.0/check"
   check = consul.Check.http(httpcheck, "30s")
   client.agent.service.register(name="datastorage",service_id=service_id,address='192.168.1.25',
                  port=8081,tags=['filestorage'],check=check)

#services unregister
def consul_service_unregister():
   client = consul.Consul()
   service_id = "datastorage-localhost:8081"
   client.agent.service.deregister(name="datastorage",service_id=service_id)

# start instance 
if __name__ == '__main__': 
   try:
      consul_service_register()
      app.run(host='0.0.0.0',port=8081)
   except RuntimeError as msg:
      if str(msg) == "Server going down":
         consul_service_unregister();
         print(msg)
      else:
         print("server stopped by accident!")
```
实际上就是给出注册的服务的id，服务名，然后给一个check的地址，然后consul的server会查询这个check的地址确认服务是否可用，在上面我用的是IP地址，因为服务搭建在docker中，如果用localhost是无法访问到的因此注册的时候要用绝对地址。  
&nbsp;&nbsp;&nbsp;&nbsp;以上代码简单的介绍了一下服务注册，由于这个代码只是提供接口，并不需要接额外的服务，因此并不需要使用服务发现模块，具体使用服务发现模块也很简单就是通过服务名或服务id查询可用的host以及port然后请求就好了，如果查询不到则说明服务不可用。