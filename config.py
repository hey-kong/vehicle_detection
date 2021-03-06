import os
import re

vehicle_template_path = 'vehicle_template.txt'
vehicle_config_path = 'vehicle.txt'

msgconv_template_path = 'msgconv_template.txt'
msgconv_config_path = 'msgconv.txt'

source_template = [
    '[source$num]\n',
    'enable=1\n',
    'type=4\n',
    'uri=$rtsp_url\n',
    'num-sources=1\n',
    'gpu-id=0\n',
    'cudadec-memtype=0\n',
    'num-extra-surfaces=2\n'
]

sensor_template = [
    '[sensor$num]\n',
    'enable=1\n',
    'type=Camera\n'
    'id=$rtsp_id\n',
    'description=Vehicle Detection\n',
    '#location=\n',
    '#coordinate=\n'
]


def gen_source(sources, urls):
    source_config = []
    for i in range(sources):
        for line in source_template:
            line = re.sub(r'\$num', str(i), line)
            line = re.sub(r'\$rtsp_url', urls[i], line)
            source_config.append(line)
        source_config.append('\n')
    return source_config


def gen_sensor(sources, ids):
    sensor_config = []
    for i in range(sources):
        for line in sensor_template:
            line = re.sub(r'\$num', str(i), line)
            line = re.sub(r'\$rtsp_id', ids[i], line)
            sensor_config.append(line)
        sensor_config.append('\n')
    return sensor_config


def gen_vehicle_config(rows, columns, sources, urls, host, port, topic, bitrate):
    vehicle_template = open(vehicle_template_path, 'r')
    vehicle = open(vehicle_config_path, 'w+')
    rrow = r'\$rows'
    row_val = str(rows)
    rcol = r'\$columns'
    col_val = str(columns)
    rbatch = r'\$batch'
    batch_val = str(sources)
    rhost = r'\$host'
    host_val = str(host)
    rport = r'\$port'
    port_val = str(port)
    rtopic = r'\$topic'
    topic_val = str(topic)
    rbitrate = r'\$bitrate'
    bitrate_val = str(bitrate)
    for line in vehicle_template.readlines():
        line = re.sub(rrow, row_val, line)
        line = re.sub(rcol, col_val, line)
        line = re.sub(rbatch, batch_val, line)
        line = re.sub(rhost, host_val, line)
        line = re.sub(rport, port_val, line)
        line = re.sub(rtopic, topic_val, line)
        line = re.sub(rbitrate, bitrate_val, line)
        vehicle.write(line)
    vehicle_template.close()
    vehicle.seek(0)
    all_lines = vehicle.readlines()
    vehicle.close()

    vehicle = open(vehicle_config_path, 'w+')
    for line in all_lines:
        if line == "{{sources}}\n":
            source_config = gen_source(sources, urls)
            vehicle.writelines(source_config)
        else:
            vehicle.write(line)
    vehicle.close()


def gen_msgconv_config(sources, ids):
    msgconv_path = open(msgconv_template_path, 'r')
    msgconv = open(msgconv_config_path, 'w+')
    for line in msgconv_path.readlines():
        if line == "{{sensor}}\n":
            sensor_config = gen_sensor(sources, ids)
            msgconv.writelines(sensor_config)
        else:
            msgconv.write(line)
    msgconv.close()


if __name__ == "__main__":
    rows = int(os.environ.get("rows"))
    columns = int(os.environ.get("columns"))
    sources = int(os.environ.get("sources"))
    ids = str(os.environ.get("rtsp_ids")).split(',')
    urls = str(os.environ.get("rtsp_urls")).split(',')
    host = str(os.environ.get("host"))
    port = int(os.environ.get("port"))
    topic = str(os.environ.get("topic"))
    bitrate = int(os.environ.get("bitrate"))
    # vehicle.txt
    gen_vehicle_config(rows, columns, sources, urls, host, port, topic, bitrate)
    # msgconv.txt
    gen_msgconv_config(sources, ids)
    os.system('deepstream-test5-app -c vehicle.txt')
