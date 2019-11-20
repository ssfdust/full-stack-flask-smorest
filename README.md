# full-stack-flask-smorest

## **特性**

-   Restful-Api
-   Jwt-Authorization
-   图片验证码
-   后台看板(adminlte)
-   文件管理
-   文件数据库软删除
-   树形闭包表
-   小型celery任务管理
-   celery自定义schedule（支持crontab与interval，且有图形界面）
-   celery进度条
-   socket-io(websocket)
-   mongodb作为日志数据库，记录所有访问的内容以及系统日志
-   rabbitmq作为队列
-   swagger(带jwt验证)
-   redoc

## **预览**

![image](https://raw.githubusercontent.com/ssfdust/full-stack-flask-rest-api/master/screenshots/swagger.png)
![image](https://raw.githubusercontent.com/ssfdust/full-stack-flask-rest-api/master/screenshots/redoc.png)
![image](https://raw.githubusercontent.com/ssfdust/full-stack-flask-rest-api/master/screenshots/dashboard.png)
![image](https://raw.githubusercontent.com/ssfdust/full-stack-flask-rest-api/master/screenshots/celery.png)
![image](https://raw.githubusercontent.com/ssfdust/full-stack-flask-rest-api/master/screenshots/files.png)

## **安装**

### **安装服务并启动**

1.  mongodb
2.  postgresql
3.  rabbitmq
4.  nginx

-   建议使用最新版

### **安装python工具以及依赖**

```bash
make
```

### **生成脚本并初始化数据库**

```bash
poetry shell
inv app.boilerplates.generate-config
inv app.db.create-pg-db-and-user
inv app.db.create-mg-db-and-user -a <mongodb_admin> -p <mongodb_passwd>
inv app.db.initdb
inv app.db.init-development-data
FLASK_ENV=testing inv app.db.initdb
FLASK_ENV=testing inv app.db.init-development-data
```

### **将域名写入到本机hosts**

```
sudo vim /etc/hosts
```

插入

```
127.0.0.1           <server_name>
```

### **为nginx添加内容**

1.  在http段新增


    ```
    include        conf.d/*.conf;
    ```

2.  在nginx.conf所在目录中不存在conf.d则创建

        ```
        sudo mkdir /etc/nginx/conf.d
        ```

3.  复制deploy/nginx/flask.conf到conf.d


        ```
        sudo cp deploy/nginx/flask.conf /etc/nginx/conf.d/
        ```

4.  重启nginx


        ```
        sudo systemctl restart nginx
        ```

### **运行服务**

```
inv app.manager
```

### **docker发布**

1.  参考docker-compose.yml修改production.toml
2.  根据production.toml生成模板配置


        ```
        inv app.boilerplates.generate-docker-compose
        ```

3.  执行


        ```
        docker-compose up
        ```

### **默认用户名密码**

-   wisdom@zero.any.else
-   zerotoany

### **访问首页**

-   &lt;server_name>/admin/login
-   &lt;server_name>/doc/redoc
-   &lt;server_name>/doc/swagger
