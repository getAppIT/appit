from docker import Client
c = Client(base_url='unix://var/run/docker.sock')
print c.containers()