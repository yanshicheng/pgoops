x = {
    "services": [
        {
            "id": "node_exporter-node01",
            "name": "node01",
            "address": "192.168.168.105",
            "port": 9100,
            "tags": ["nodes"],
            "checks": [
                {"http": "http://192.168.168.105:9100/metrics", "interval": "5s"}
            ],
        },
        {
            "id": "node_exporter-node02",
            "name": "node02",
            "address": "192.168.168.102",
            "port": 9100,
            "tags": ["nodes"],
            "checks": [
                {"http": "http://192.168.168.102:9100/metrics", "interval": "5s"}
            ],
        },
    ]
}
print(x)
