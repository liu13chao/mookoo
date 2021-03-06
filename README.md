# MOOKOO

MooKoo是一个基于Python的Mock http server

## 安装

### 使用pip安装

``` bash
pip install mookoo
mkdir mock1; cd mock1
# Edit mock files
```

### 手工安装

``` bash
mkdir mock1; cd mock1
git clone https://github.com/gaorx/mookoo.git && rm -rf mookoo/.git
# Edit mock files
```

## 起步

在`mock1`目录中，编辑`mock.py`

``` python
from mookoo import *
GET('/hello').json({"message": "Hello MooKoo!"})
run()
```

然后在shell中执行

``` bash
python mock.py
# 也可以设定端口
# python mock.py -p 9928
```

然后在浏览器中就访问`http://localhost:7928/hello`，就可以看到

``` json
{"message": "Hello Mookoo"}
```

也可以访问`http://localhost:7928/+mookoo`查看此帮助文件



## 进阶

### 动态加载文件

在`mock1`目录中，创建`hello.json`，然后编辑它，然后使用下面的代码动态加载

``` python
GET('/hello').load_json('hello.json')
```

### 修改`Status`和`Header`

``` python
# 定制Status
GET('/404').html('<h1>Not found</h1>', status=404)

# 加入Header
GET('/custom_header').text("Press F12", header={"My-Header": "HeaderContent"})

# 修改content_type
GET('/custom_content_type').text("<h1>Press F12</h1>", content_type='text/html')
```

### 静态文件

将一张在`mock1`目录中复制一张图片`hello.jpg`

``` python
GET('/image').static_file('hello.jpg')
```

### 动态响应

``` python
@GET('/dynamic/<sub>')
def _dynamic(sub):
	response.content_type = 'text/plain'
    return "Sub path is %s, query_string is '%s'" % (sub, request.query_string)
```

### 动态JSON

在`mock1`目录中，创建`hello.json.py`，内容为:

``` python
JSON = {
	"message": "Python json",
    "query_string": request.query_string,
}
```

然后使用下面的代码加载:

``` python
GET('/dynamic_json').load_json('hello.json.py')
```

### 重定向

``` python
GET('/redirect').redirect('https://github.com/gaorx/mookoo')
```

### 代理

``` python
GET('/http_rfc').proxy('https://tools.ietf.org/rfc/rfc2616.txt')
```

### 静态目录

``` python
@mookoo.GET('/static/<filename:path>')
def _static_dir(filename):
    return mookoo.static_file(os.path.join('static_dir', filename))
```



