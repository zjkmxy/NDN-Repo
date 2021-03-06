# NDN-Repo

A quick-and-dirty Named Data Networking (NDN) Repo implementation using [python-ndn](https://github.com/zjkmxy/python-ndn).

## Prerequisites

* Required: Python 3.6+
* Required: [python-ndn](https://github.com/zjkmxy/python-ndn) - A Named Data Networking client library with AsyncIO support in Python 3.
* Required: [NFD](https://github.com/named-data/NFD) - Named Data Networking Forwarding Daemon
* Optional: The default backend database is SQLite3. If you want to change the default database, you need one of:
  * [LevelDB](https://github.com/google/leveldb) - Fast key-value storage library
  * [MongoDB](https://www.mongodb.com) - A document-oriented database, and [PyMongo](https://api.mongodb.com/python/current/) - MongoDB Python interface

## Getting Started

For macOS and Ubuntu:

```bash
git clone https://github.com/JonnyKong/NDN-Repo.git

# 1) Install dependencies
pip3 install -r requirements.txt

# 2) Run unit tests
make test

# 3) Install NDN-Repo
sudo make install

# 4.1) Start a repo instance with systemd (Ubuntu)
sudo systemctl start ndn-repo.service
# 4.2) ... or start a repo instance directly
python3 main.py

# 5) Check repo status (Ubuntu)
sudo journalctl -u ndn-repo.service

# Insert a file into the repo
cd src/clients && python3 putfile.py -r <repo_name> -f <path_to_file> -n <filename_in_repo>

# Fetch a file from the repo
cd src/clients && python3 getfile.py -r <repo_name> -n <filename_in_repo>
```

## TODO

- [x] TCP Bulk Insertion functionality, tested using NDNCERT
- [x] Control Center basic Web interface
- [x] Control Center backend: list Data, delete Data, display up-to-date Repo status, commands (stop, start, restart)
- [x] HTTP Get Data Demo program (http_get_data.py in directory `src`)
- [x] Add an instructions page
- [x] Insert check command
- [x] Delete command
- [x] Delete check command
- [ ] Add command validator for `handles`
- [ ] Finalize database implementation for Google Cloud DataStore. (MongoDB is not very convenient to configure)
- [ ] Now we have HTTP get Data endpoint. We might want to add a TCP get Data. This introduces design questions, e.g. Do we use port 7376 for Data fetching, or we use a different port?
- [ ] Configure a PyNDN-Repo Docker for easier deployment
- [ ] Nail down protocol design
- [ ] Implement Trust Schema for Data and command verification
- [ ] Add more demo programs, and improve documentations
