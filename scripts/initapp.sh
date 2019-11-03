if [ ! -e "./inited_app" ];then
    touch ./inited_app
    inv app.init.initdb
    inv app.init.init-development-data
fi
inv app.run -p 5000 -h 0.0.0.0
