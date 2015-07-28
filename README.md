weibo
========

基于Flask的微博系统，实现了基本的微博功能。

数据库采用SQLite3，用户头像采用[http://www.gravatar.com](http://en.gravatar.com/site/implement/hash/)提供的用邮箱的哈希值生成的url。

功能:

	* 用户注册、登录
	* 发表、转发微博
	* 查看用户资料
	* 查看用户关注、粉丝名单
	* 查看我的圈子的动态
	* 采用d3.js展示信息传播过程
	* 采用highcharts展示信息演化速度

DEMO:

<img src="images/img1.png" alt="img1">
<img src="images/img2.png" alt="img2">
<img src="images/image3.png" alt="img3">

架构环境：

	1.python2.7

	2.nginx+uwsgi-python-plugin

	3.install sqlachmey
	
	4.d3.js

功能框架：

	mywebsite.py：后台application主程序

	schema.sql：数据库

	build_graph_curve.py：构建信息传播基础拓扑，采用networkx库处理数据，构建信息演化动态图，采用Numpy开源库处理数据
	
	data:主要存储的是处理后的转发关系数据，我们将二度转发网转换为一度连接网，这样在展示的时候可以看到源消息的转发过程。

信息传播数据：

	目前采用的数据是从新浪微博上实时爬取的，这里主要爬取的是某条消息的转发、评论列表。这个可以参考我的另一个项目sina_weibo_crawler.

后续工作：
	
	目前在展示传播网的过程中，js加载的时候是将全部的图片及关系加载进来，实际上在test.html中可以一层一层的加载关系网，目前这部分的工作还在进行中。
	