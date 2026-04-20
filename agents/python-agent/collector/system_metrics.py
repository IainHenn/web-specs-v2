import asyncio
import psutil
import json

from ping3 import ping
import ifcfg 
import pynvml


def get_gpu_stats():
    gpu_info = {}
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        gpus = {}
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode()
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpus[f"gpu_{i}"] = {
                'name': name,
                'memory_total': {'value': memory.total, 'unit': 'bytes'},
                'memory_used': {'value': memory.used, 'unit': 'bytes'},
                'memory_free': {'value': memory.free, 'unit': 'bytes'},
                'temperature': {'value': temperature, 'unit': 'celsius'},
                'gpu_utilization': {'value': utilization.gpu, 'unit': 'percent'},
                'memory_utilization': {'value': utilization.memory, 'unit': 'percent'}
            }
        gpu_info['vendor'] = 'NVIDIA'
        gpu_info['gpus'] = gpus
        pynvml.nvmlShutdown()
    except Exception as e:
        gpu_info['error'] = str(e)
    return gpu_info

def get_ping():
    try:
        interfaces = ifcfg.interfaces()
        ip = None
        for iface in interfaces.values():
            if 'inet' in iface and iface['inet'] != '127.0.0.1':
                ip = iface['inet']
                break
        if ip:
            result = ping(ip)
            if result:
                # ping3 returns seconds; convert to microseconds for resolution
                return {'value': result * 1000000, 'unit': 'microseconds'}
            return None
        return None
    except Exception as e:
        print(f"error: {e}")
        return None

def gather_cpu_times():
    cpu_times = psutil.cpu_times(percpu=True)

    user_time = {f"core_{i+1}": core[0] for i, core in enumerate(cpu_times)}
    system_time = {f"core_{i+1}": core[1] for i, core in enumerate(cpu_times)}
    idle_time = {f"core_{i+1}": core[2] for i, core in enumerate(cpu_times)}
    
    return user_time, system_time, idle_time

def gather_cpu_percents():
    cpu_percents = psutil.cpu_percent(percpu=True)
    return {f"core_{i+1}": percent for i, percent in enumerate(cpu_percents)}

def gather_virtual_memory_stats():
    virtual_memory = psutil.virtual_memory()
    return virtual_memory[1], virtual_memory[2], virtual_memory[3]

def gather_swap_memory_stats():
    swap_memory = psutil.swap_memory()
    return swap_memory[1], swap_memory[2], swap_memory[3]

def get_disk_usage():
    disk_partitions = psutil.disk_partitions()
    disk_usage_info = {}
    for partition in disk_partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage_info[partition.device] = {
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": {'value': usage.total, 'unit': 'bytes'},
                "used": {'value': usage.used, 'unit': 'bytes'},
                "free": {'value': usage.free, 'unit': 'bytes'},
                "percent": {'value': usage.percent, 'unit': 'percent'}
            }
        except PermissionError:
            continue
    return disk_usage_info

# Windows needs diskperf -y ran in cmd.exe
def get_disk_io_counters():
    raw_disks = psutil.disk_io_counters(perdisk=True)
    result = {}
    for key, value in raw_disks.items():
        result[key] = {
            'read_count': {'value': value.read_count, 'unit': 'count'},
            'write_count': {'value': value.write_count, 'unit': 'count'},
            'read_bytes': {'value': value.read_bytes, 'unit': 'bytes'},
            'write_bytes': {'value': value.write_bytes, 'unit': 'bytes'},
            'read_time': {'value': value.read_time, 'unit': 'milliseconds'},
            'write_time': {'value': value.write_time, 'unit': 'milliseconds'},
        }
    return result

def collect_metrics():

    system_info = {}

    # CPU
    system_info['cpu'] = {}
    user_time, system_time, idle_time = gather_cpu_times()
    system_info['cpu']['user_time'] = {k: {'value': v, 'unit': 'seconds'} for k, v in user_time.items()}
    system_info['cpu']['system_time'] = {k: {'value': v, 'unit': 'seconds'} for k, v in system_time.items()}
    system_info['cpu']['idle_time'] = {k: {'value': v, 'unit': 'seconds'} for k, v in idle_time.items()}
    system_info['cpu']['percent'] = {k: {'value': v, 'unit': 'percent'} for k, v in gather_cpu_percents().items()}

    # Memory
    system_info['memory'] = {}
    available_memory, percent_usage, used_memory = gather_virtual_memory_stats()
    system_info['memory']['available_memory'] = {'value': available_memory, 'unit': 'bytes'}
    system_info['memory']['memory_percent_usage'] = {'value': percent_usage, 'unit': 'percent'}
    system_info['memory']['used_memory'] = {'value': used_memory, 'unit': 'bytes'}

    # Swap memory
    system_info['swap_memory'] = {}
    swap_used_memory, swap_free_memory, swap_percent_usage = gather_swap_memory_stats()
    system_info['swap_memory']['used_memory'] = {'value': swap_used_memory, 'unit': 'bytes'}
    system_info['swap_memory']['free_memory'] = {'value': swap_free_memory, 'unit': 'bytes'}
    system_info['swap_memory']['percent_usage'] = {'value': swap_percent_usage, 'unit': 'percent'}

    # Disk usage
    system_info['disk_usage'] = get_disk_usage()

    # IO
    system_info['io'] = get_disk_io_counters()

    # GPU
    system_info['gpu'] = get_gpu_stats()

    # Ping (latency to primary interface)
    system_info['ping'] = get_ping()

    return system_info

async def async_collect_metrics():
    loop = asyncio.get_running_loop()
    
    # Run the blocking function in a separate thread
    metrics = await loop.run_in_executor(None, collect_metrics)
    return metrics