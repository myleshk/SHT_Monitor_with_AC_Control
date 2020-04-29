module.exports = {
  "apps": [{
    "name": "temp_hum_monitor",
    "script": "main.py",
    "instances": "1",
    "wait_ready": true,
    "autorestart": false,
    "max_restarts": 5,
    "interpreter": "./venv/bin/python",
  }]
};
