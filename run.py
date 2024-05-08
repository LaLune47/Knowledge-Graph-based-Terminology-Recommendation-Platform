from app import app as apps,db,app_tools
db.create_all()

if __name__ == "__main__":
    app_tools.SocketIo.run(apps, host='0.0.0.0', port=8000, debug=True)
