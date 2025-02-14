import psutil
import socket

def get_all_ips():
    interfaces = psutil.net_if_addrs()
    ip_addresses = {}

    for interface, addresses in interfaces.items():
        ip_list = []
        for addr in addresses:
            if addr.family == socket.AF_INET:  # IPv4
                ip_list.append(addr.address)
            elif addr.family == socket.AF_INET6 and '%' not in addr.address:  # IPv6 (excluding link-local)
                ip_list.append(addr.address)

        if ip_list:
            ip_addresses[interface] = ip_list

    return ip_addresses

if __name__ == "__main__":
    all_ips = get_all_ips()
    for interface, ips in all_ips.items():
        print(f"{interface}:")
        for ip in ips:
            print(f"  - {ip}")
