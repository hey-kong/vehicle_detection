import os
import re

template_path = 'vehicle_template.txt'
config_path = 'vehicle.txt'

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


def gen_source(sources, urls):
    source_config = []
    for i in range(sources):
        for line in source_template:
            line = re.sub(r'\$num', str(i), line)
            line = re.sub(r'\$rtsp_url', urls[i], line)
            source_config.append(line)
        source_config.append('\n')
    return source_config


def gen_config(rows, columns, sources, urls):
    vehicle_template = open(template_path, 'r')
    vehicle = open(config_path, 'w+')
    row = r'\$rows'
    row_val = str(rows)
    col = r'\$columns'
    col_val = str(columns)
    batch = r'\$batch'
    batch_val = str(sources)
    for line in vehicle_template.readlines():
        line = re.sub(row, row_val, line)
        line = re.sub(col, col_val, line)
        line = re.sub(batch, batch_val, line)
        vehicle.write(line)
    vehicle_template.close()
    vehicle.seek(0)
    all_lines = vehicle.readlines()
    vehicle.close()

    vehicle = open(config_path, 'w+')
    for line in all_lines:
        if line == "{{sources}}\n":
            source_config = gen_source(sources, urls)
            vehicle.writelines(source_config)
        else:
            vehicle.write(line)
    vehicle.close()


if __name__ == "__main__":
    rows = int(os.environ.get("rows"))
    columns = int(os.environ.get("columns"))
    sources = int(os.environ.get("sources"))
    urls = str(os.environ.get("rtsp_urls")).split(',')
    gen_config(rows, columns, sources, urls)
    os.system('deepstream-app -c vehicle.txt')
